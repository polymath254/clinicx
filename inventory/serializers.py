from rest_framework import serializers
from .models import Supplier, Drug, PurchaseOrder

class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = ['id', 'name', 'email', 'phone', 'created_at']
        read_only_fields = ['id', 'created_at']

class DrugSerializer(serializers.ModelSerializer):
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)
    needs_reorder  = serializers.BooleanField(read_only=True)

    class Meta:
        model = Drug
        fields = [
            'id', 'name', 'description', 'price',
            'quantity', 'reorder_threshold', 'needs_reorder',
            'supplier', 'supplier_name', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'needs_reorder', 'created_at', 'updated_at', 'supplier_name']

class PurchaseOrderSerializer(serializers.ModelSerializer):
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)
    drug_name     = serializers.CharField(source='drug.name', read_only=True)

    class Meta:
        model = PurchaseOrder
        fields = [
            'id', 'supplier', 'supplier_name',
            'drug', 'drug_name',
            'quantity', 'status',
            'created_at', 'delivered_at',
        ]
        read_only_fields = ['id', 'supplier_name', 'drug_name', 'created_at', 'delivered_at']
