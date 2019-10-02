from django.conf import settings

from sberbank.models import Payment, Status
from sberbank.service import BankService


def check_payments():
    unchecked_payments = Payment.objects.filter(
        status=Status.PENDING, bank_id__isnull=False)
    for payment in unchecked_payments:
        BankService(settings.MERCHANT_KEY).check_status(payment.uid)
