from rest_framework import serializers
from .models import Invoice, Payment

class InvoiceSerializer(serializers.ModelSerializer):
    patient_email = serializers.EmailField(source='patient.email', read_only=True)
    status        = serializers.CharField(read_only=True)

    class Meta:
        model = Invoice
        fields = ['id', 'patient', 'patient_email', 'amount', 'status', 'created_at', 'due_date']
        read_only_fields = ['id', 'status', 'created_at', 'patient_email']

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Invoice amount must be greater than zero.")
        return value


class PaymentSerializer(serializers.ModelSerializer):
    invoice_id   = serializers.IntegerField(source='invoice.id', read_only=True)
    amount       = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    status       = serializers.CharField(read_only=True)

    class Meta:
        model = Payment
        fields = [
            'id', 'invoice', 'invoice_id', 'amount',
            'mpesa_checkout_request_id', 'mpesa_receipt_number',
            'status', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'amount', 'mpesa_checkout_request_id',
                            'mpesa_receipt_number', 'status', 'created_at', 'updated_at']
