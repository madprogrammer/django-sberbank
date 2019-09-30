from hashlib import sha256
import hmac
import json

from collections import OrderedDict

from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from rest_framework.response import Response
from rest_framework.views import APIView

from sberbank.models import Payment, LogEntry, Status
from sberbank.service import BankService
from sberbank.serializers import PaymentSerializer


class StatusView(APIView):
    @staticmethod
    def get(request, uid=None):
        try:
            payment = Payment.objects.get(uid=uid)
        except Payment.DoesNotExist:
            return HttpResponse(status=404)
        return Response({"status": Status(payment.status).name})


class BindingsView(APIView):
    @staticmethod
    def get(request, client_id=None):
        svc = BankService(settings.MERCHANT_KEY)
        return Response(svc.get_bindings(client_id))

class BindingView(APIView):
    authentication_classes = []

    @staticmethod
    def delete(request, binding_id=None):
        svc = BankService(settings.MERCHANT_KEY)
        svc.deactivate_binding(binding_id)
        return HttpResponse(status=200)

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(BindingView, self).dispatch(*args, **kwargs)


class GetHistoryView(APIView):
    @staticmethod
    def get(request, client_id=None, format=None):
        payments = Payment.objects.filter(client_id=client_id, status=Status.SUCCEEDED).order_by('-updated')
        serializer = PaymentSerializer(payments, many=True)
        return Response(serializer.data)


def callback(request):
    data = OrderedDict(sorted(request.GET.items(), key=lambda x: x[0]))

    try:
        payment = Payment.objects.get(bank_id=data.get('mdOrder'))
    except Payment.DoesNotExist:
        return HttpResponse(status=200)

    merchant = settings.MERCHANTS.get(settings.MERCHANT_KEY)
    hash_key = merchant.get('hash_key')

    if hash_key:
        check_str = ''

        for key, value in data.items():
            if key != 'checksum':
                check_str += "%s;%s;" % (key, value)

        checksum = hmac.new(hash_key.encode(), check_str.encode(), sha256) \
            .hexdigest().upper()

        LogEntry.objects.create(
            action="callback",
            bank_id=payment.bank_id,
            payment_id=payment.uid,
            response_text=json.dumps(request.GET),
            checksum=checksum
        )

        if checksum != data.get('checksum'):
            payment.status = Status.FAILED
            payment.save()
            return HttpResponseBadRequest('Checksum check failed')

    if int(data.get('status')) == 1:
        payment.status = Status.SUCCEEDED
    elif int(data.get('status')) == 0:
        payment.status = Status.FAILED

    payment.save()

    return HttpResponse(status=200)


def redirect(request, kind=None):
    try:
        payment = Payment.objects.get(bank_id=request.GET.get('orderId'))
    except Payment.DoesNotExist:
        return HttpResponse(status=404)

    svc = BankService(settings.MERCHANT_KEY)
    svc.check_status(payment.uid)

    LogEntry.objects.create(
        action="redirect_%s" % kind,
        bank_id=payment.bank_id,
        payment_id=payment.uid,
        response_text=json.dumps(request.GET),
    )

    svc.check_bind_refund(payment)

    merchant = settings.MERCHANTS.get(settings.MERCHANT_KEY)
    return HttpResponseRedirect("%s?payment=%s" % (merchant["app_%s_url" % kind], payment.uid))
