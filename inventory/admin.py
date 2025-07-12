from django.contrib import admin
from .models import Supplier, Drug, PurchaseOrder

@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display   = ('name','email','phone','created_at')
    search_fields  = ('name','email')
    ordering       = ('name',)

@admin.register(Drug)
class DrugAdmin(admin.ModelAdmin):
    list_display   = ('name','supplier','quantity','reorder_threshold','needs_reorder')
    search_fields  = ('name','supplier__name')
    list_filter    = ('supplier',)
    readonly_fields= ('needs_reorder',)

@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display   = ('id','drug','supplier','quantity','status','created_at','delivered_at')
    list_filter    = ('status','supplier')
    search_fields  = ('drug__name','supplier__name')
    actions        = ['mark_as_delivered']

    def mark_as_delivered(self, request, queryset):
        for po in queryset:
            if po.status != PurchaseOrder.STATUS_DELIVERED:
                po.mark_delivered()
    mark_as_delivered.short_description = "Mark selected Purchase Orders as delivered"
