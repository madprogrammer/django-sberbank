from datetime import timedelta

from celery.task import periodic_task
from django.conf import settings

from sberbank.models import Payment, Status
from sberbank.service import BankService


@periodic_task(run_every=timedelta(minutes=20))
def check_payments():
    unchecked_payments = Payment.objects.filter(
        status=Status.PENDING, bank_id__isnull=False)
    for payment in unchecked_payments:
        BankService(settings.MERCHANT_KEY).check_status(payment.uid)
