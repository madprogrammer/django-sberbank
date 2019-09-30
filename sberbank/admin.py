from django.contrib import admin
from django.utils.translation import ugettext as _

from sberbank.models import Payment, LogEntry


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        'uid', 'bank_id', 'amount', 'status', 'created', 'updated',
    )
    list_filter = ('status',)
    search_fields = (
        'uid', 'bank_id', 'amount'
    )

    readonly_fields = (
        'created', 'updated', 'uid', 'bank_id', 'client_id', 'amount',
        'status', 'method', 'details', 'error_code', 'error_message'
    )

    fieldsets = (
        (
            None,
            {
                'fields': [
                    ('uid', 'bank_id', 'client_id'),
                    'status', 'method',
                    ('amount',),
                ]
            }
        ),
        (
            _('More details'),
            {
                'classes': ('collapse',),
                'fields': ['details', 'error_code', 'error_message']
            }
        ),
    )


@admin.register(LogEntry)
class LogEntryAdmin(admin.ModelAdmin):
    list_display = (
        'uid', 'payment_id', 'bank_id', 'action', 'created',
    )
    search_fields = (
        'uid', 'bank_id', 'payment_id', 'action'
    )

    readonly_fields = (
        'created', 'uid', 'payment_id', 'bank_id', 'action',
        'request_text', 'response_text', 'checksum')

    fieldsets = (
        (
            None,
            {
                'fields': [
                    ('uid', 'payment_id', 'bank_id'),
                    'action',
                    'request_text',
                    'response_text',
                ]
            }
        ),
    )
