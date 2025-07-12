from django.contrib import admin
from .models import Invoice, Payment

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display   = ('id', 'patient', 'amount', 'status', 'created_at', 'due_date')
    list_filter    = ('status',)
    search_fields  = ('patient__email',)
    actions        = ['mark_paid', 'mark_cancelled']

    def mark_paid(self, request, queryset):
        for inv in queryset:
            inv.mark_paid()
    mark_paid.short_description = "Mark selected invoices as paid"

    def mark_cancelled(self, request, queryset):
        for inv in queryset:
            inv.mark_cancelled()
    mark_cancelled.short_description = "Mark selected invoices as cancelled"


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display   = ('id', 'invoice', 'amount', 'status', 'created_at')
    list_filter    = ('status',)
    search_fields  = ('invoice__id', 'mpesa_checkout_request_id')
