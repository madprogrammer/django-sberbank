from django.contrib import admin

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

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(LogEntry)
class LogEntryAdmin(admin.ModelAdmin):
    list_display = (
        'uid', 'payment_id', 'bank_id', 'action', 'created',
    )
    search_fields = (
        'uid', 'bank_id', 'payment_id', 'action'
    )

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False
