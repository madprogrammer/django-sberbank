import uuid
from enum import IntEnum

from jsonfield import JSONField
from django.db import models
from django.utils.translation import ugettext as _

from sberbank import sberbank_settings


class Choice(IntEnum):
    @classmethod
    def choices(cls):
        return [(x.value, x.name) for x in cls]


class Status(Choice):
    CREATED = 0
    PENDING = 1
    SUCCEEDED = 2
    FAILED = 3
    REFUNDED = 4

    def __str__(self):
        return str(self.value)


class Method(Choice):
    UNKNOWN = 0
    WEB = 1
    APPLE = 2
    GOOGLE = 3

    def __str__(self):
        return str(self.value)


class Payment(models.Model):
    """
    details JSON fields:
        username
        currency
        success_url
        fail_url
        session_timeout
        page_view
        redirect_url
    """

    uid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    bank_id = models.UUIDField(_("bank ID"), null=True, blank=True, db_index=True)
    amount = models.DecimalField(_("amount"), max_digits=128, decimal_places=2)
    order_number = models.CharField(
        'Номер заказа', max_length=64, editable=False,
        default=sberbank_settings.generate_order_number
    )
    error_code = models.PositiveIntegerField(_("error code"), null=True, blank=True)
    error_message = models.TextField(_("error message"), null=True, blank=True)
    status = models.PositiveSmallIntegerField(_("status"), choices=Status.choices(),
                                              default=Status.CREATED, db_index=True)
    details = JSONField(_("details"), blank=True, null=True)
    client_id = models.TextField(_("client ID"), null=True, blank=True)
    method = models.PositiveSmallIntegerField(_("method"), choices=Method.choices(),
                                              default=Method.UNKNOWN, db_index=True)
    created = models.DateTimeField(_("created"), auto_now_add=True, db_index=True)
    updated = models.DateTimeField(_("modified"), auto_now=True, db_index=True)

    class Meta:
        ordering = ['-updated']
        verbose_name = _('payment')
        verbose_name_plural = _('payments')

    def __str__(self):
        return "%s: %s" % (Status(self.status).name, self.amount)


class LogEntry(models.Model):
    uid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    payment_id = models.UUIDField(_("payment ID"), null=True, blank=True, db_index=True)
    bank_id = models.UUIDField(_("bank payment ID"), null=True, blank=True, db_index=True)
    action = models.CharField(_("action"), max_length=100, db_index=True)
    request_text = models.TextField(_("request text"), null=True, blank=True)
    response_text = models.TextField(_("response text"), null=True, blank=True)
    created = models.DateTimeField(_("created"), auto_now_add=True, db_index=True)
    checksum = models.CharField(max_length=256, null=True, blank=True, db_index=True)

    class Meta:
        ordering = ['-created']
        verbose_name = _('log entry')
        verbose_name_plural = _('log entries')
