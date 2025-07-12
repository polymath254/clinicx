from django.contrib import admin
from .models import Order

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display   = ('id','patient','prescription','drug','quantity','status','created_at')
    list_filter    = ('status','created_at','drug')
    search_fields  = ('patient__email','prescription__id','drug__name')
    actions        = ['mark_dispensed','mark_cancelled']

    def mark_dispensed(self, request, queryset):
        for order in queryset:
            order.process()
    mark_dispensed.short_description = "Process and mark selected orders as dispensed"

    def mark_cancelled(self, request, queryset):
        queryset.update(status=Order.STATUS_CANCELLED)
    mark_cancelled.short_description = "Mark selected orders as cancelled"

