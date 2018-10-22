import json
import base64
from decimal import Decimal, DecimalException

import requests
from django.conf import settings
from django.utils.translation import ugettext as _

from sberbank.exceptions import NetworkException, ProcessingException, \
    PaymentNotFoundException
from sberbank.models import Payment, LogEntry, Status
from sberbank.util import system_name

class BankService(object):
    __default_session_timeout = 1200
    __default_currency_code = 643
    __default_gateway_address = 'https://3dsec.sberbank.ru/payment'

    def __init__(self, merchant_id):
        if getattr(settings, 'ENVIRONMENT', 'development') == 'production':
            self.__default_gateway_address = \
                'https://securepayments.sberbank.ru/payment'
        self._get_credentials(merchant_id)

    def _get_credentials(self, merchant_id):
        settings_merchant_key = "MERCHANTS"

        merchants = getattr(settings, settings_merchant_key, None)
        if merchants is None:
            raise KeyError(
                "Key %s not found in settings.py" % settings_merchant_key)

        self.merchant = merchants.get(merchant_id, None)
        if self.merchant is None:
            raise KeyError(
                "Merchant key %s not found in %s" % (
                    merchant_id, settings_merchant_key))

        for field_name in ["username", "password"]:
            if self.merchant.get(field_name, None) is None:
                raise KeyError(
                    "Field '%s' not found in %s->%s" % (
                        field_name, settings_merchant_key, merchant_id))

    def mobile_pay(self, amount, token, ip, **kwargs):
        currency = self.merchant.get('currency', self.__default_currency_code)
        details = kwargs.get('details', {})
        method = "applepay/payment"

        try:
            decoded_token = json.loads(base64.b64decode(token).decode())
            if "encryptedMessage" in decoded_token:
                method = "google/payment"
        except:
            raise TypeError("Failed to decode payment token")

        try:
            amount = Decimal(str(amount))
        except (ValueError, DecimalException):
            raise TypeError(
                "Wrong amount type, passed {} ({}) instead of decimal".format(amount, type(amount)))

        payment = Payment(amount=amount, details={
            'username': self.merchant.get("username"),
            'currency': currency
        })

        if kwargs.get('params'):
            payment.details.update(kwargs.get('params'))

        payment.details.update(details)
        payment.save()

        data = {
            'merchant': self.merchant.get("username"),
            'orderNumber': payment.uid.hex,
            'amount': int(amount * 100),
            'paymentToken': token,
            'ip': ip
        }
        if kwargs.get('params'):
            data.update({'additionalParameters': kwargs.get('params')})
        if kwargs.get('description'):
            data.update({'description': kwargs.get('description')})

        return self.execute_request(data, method, payment)

    def pay(self, amount, preauth=False, **kwargs):
        session_timeout = self.merchant.get('session_timeout', self.__default_session_timeout)
        currency = self.merchant.get('currency', self.__default_currency_code)
        fail_url = kwargs.get('fail_url', self.merchant.get('fail_url'))
        success_url = kwargs.get('success_url', self.merchant.get('success_url'))
        client_id = kwargs.get('client_id')
        page_view = kwargs.get('page_view', 'DESKTOP')
        details = kwargs.get('details', {})
        description = kwargs.get('description')
        method = 'rest/register' if not preauth else "rest/registerPreAuth"

        if success_url is None:
            raise ValueError("success_url is not set")

        try:
            amount = Decimal(str(amount))
        except (ValueError, DecimalException):
            raise TypeError(
                "Wrong amount type, passed {} ({}) instead of decimal".format(amount, type(amount)))

        payment = Payment(amount=amount, client_id=client_id, details={
            'username': self.merchant.get("username"),
            'currency': currency,
            'success_url': success_url,
            'fail_url': fail_url,
            'session_timeout': session_timeout,
            'client_id': client_id
        })

        payment.details.update(details)
        payment.save()

        data = {
            'orderNumber': payment.uid.hex,
            'amount': int(amount * 100),
            'returnUrl': success_url,
            'failUrl': fail_url,
            'sessionTimeoutSecs': session_timeout,
            'pageView': page_view,
        }
        if kwargs.get('params'):
            data.update({'jsonParams': json.dumps(kwargs.get('params'))})
        if kwargs.get('client_id'):
            data.update({'clientId': client_id})
        if kwargs.get('description'):
            data.update({'description': description})

        response = self.execute_request(data, method, payment)
 
        payment.bank_id = response.get('orderId')
        payment.status = Status.PENDING
        payment.details.update({'redirect_url': response.get('formUrl')})
        if kwargs.get('params'):
            payment.details.update(kwargs.get('params'))
        payment.save()

        return payment, payment.details.get("redirect_url")

    def bind_refund(self, client_id):
        return self.pay(1.0, client_id=client_id,
            method="registerPreAuth", page_view="bind", details={"bind_refund": True},
            description=_("card binding"))

    def check_bind_refund(self, payment):
        if payment.details.get('bind_refund', False) and \
            payment.status in (Status.PENDING, Status.SUCCEEDED):
            self.reverse(payment)

    def reverse(self, payment):
        return self.execute_request({'orderId': str(payment.bank_id)}, "rest/reverse", payment)

    def check_status(self, payment_uid):
        try:
            payment = Payment.objects.get(pk=payment_uid)
        except Payment.DoesNotExist:
            raise PaymentNotFoundException()

        data = {'orderId': str(payment.bank_id)}
        response = self.execute_request(data, "rest/getOrderStatusExtended", payment)

        if response.get('orderStatus') == 2:
            payment.status = Status.SUCCEEDED
            payment.details.update({"pan": response['cardAuthInfo']['pan']})
        elif response.get('orderStatus') in [3, 5, 6]:
            payment.status = Status.FAILED

        payment.save(update_fields=['status', 'details'])

    def get_bindings(self, client_id):
        def convert(entry):
            return {
                'binding': entry['bindingId'],
                'masked_pan': entry['maskedPan'],
                'expiry_date': entry['expiryDate'],
                'system': system_name(entry['maskedPan'])
            }
        try:
            response = self.execute_request({"clientId": client_id}, "rest/getBindings")
            return list(map(convert, response.get('bindings')))
        except ProcessingException as exc:
            if exc.error_code == 2:
                return []

    def deactivate_binding(self, binding_id):
        self.execute_request({'bindingId': binding_id}, "rest/unBindCard")

    def execute_request(self, data, method, payment=None):
        data.update({
            "userName": self.merchant.get('username'),
            'password': self.merchant.get('password')
        })
        try:
            response = requests.post(
                '{}/{}.do'.format(self.__default_gateway_address, method), data)
        except (requests.ConnectTimeout,
                requests.ConnectionError,
                requests.HTTPError):
            if payment:
                payment.status = Status.FAILED
                payment.save()
            raise NetworkException(payment.uid if payment else None)

        data.update({'password': '****'})
        LogEntry.objects.create(action=method,
            bank_id=payment.bank_id if payment else None,
            payment_id=payment.uid if payment else None,
            response_text=response.text, request_text=json.dumps(data))

        if response.status_code != 200:
            if payment:
                payment.status = Status.FAILED
                payment.save()
            raise ProcessingException(payment.uid if payment else None, response.text,
                                      response.status_code)
        try:
            response = response.json()
        except (ValueError, UnicodeDecodeError):
            if payment:
                payment.status = Status.FAILED
                payment.save()
            raise ProcessingException(payment.uid if payment.uid else None)


        if int(response.get('errorCode', 0)) != 0:
            if payment:
                payment.error_code = response.get('errorCode')
                payment.error_message = response.get('errorMessage')
                payment.status = Status.FAILED
                payment.save()
            raise ProcessingException(payment.uid if payment else None, response.get('errorMessage'),
                                      response.get('errorCode'))

        return response
