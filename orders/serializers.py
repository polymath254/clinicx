from rest_framework import serializers
from django.db import transaction
from .models import Order
from prescriptions.models import PrescriptionDrug
from inventory.models import Drug

class OrderSerializer(serializers.ModelSerializer):
    patient_email    = serializers.EmailField(source='patient.email', read_only=True)
    prescription_id  = serializers.IntegerField(source='prescription.id', read_only=True)
    drug_name        = serializers.CharField(source='drug.name', read_only=True)
    status           = serializers.CharField(read_only=True)

    class Meta:
        model = Order
        fields = [
            'id',
            'patient', 'patient_email',
            'prescription', 'prescription_id',
            'drug', 'drug_name',
            'quantity',
            'status',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'patient_email', 'prescription_id', 'drug_name', 'status', 'created_at', 'updated_at']

    def validate(self, data):
        # Ensure the logged-in pharmacist sets the patient to the prescription's patient
        request = self.context.get('request')
        prescription = data.get('prescription')
        if request and request.user.role == 'pharmacist':
            data['patient'] = prescription.patient

        # Validate drug vs prescription
        drug = data.get('drug')
        pd_qs = PrescriptionDrug.objects.filter(prescription=prescription, drug=drug)
        if not pd_qs.exists():
            raise serializers.ValidationError("Drug not in prescription.")
        pd = pd_qs.get()

        # Validate quantity <= prescribed
        if data.get('quantity') > pd.quantity:
            raise serializers.ValidationError("Cannot dispense more than prescribed.")
        return data

    def create(self, validated_data):
        order = super().create(validated_data)
        # Immediately process stock & status
        order.process()
        return order

