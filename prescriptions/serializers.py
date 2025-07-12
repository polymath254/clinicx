from rest_framework import serializers
from .models import Prescription, PrescriptionDrug
from django.utils import timezone

class PrescriptionDrugSerializer(serializers.ModelSerializer):
    drug_name = serializers.CharField(source='drug.name', read_only=True)

    class Meta:
        model = PrescriptionDrug
        fields = ['id', 'drug', 'drug_name', 'dosage', 'quantity']

class PrescriptionSerializer(serializers.ModelSerializer):
    doctor_email = serializers.EmailField(source='doctor.email', read_only=True)
    patient_email = serializers.EmailField(source='patient.email', read_only=True)
    drugs = PrescriptionDrugSerializer(many=True)

    class Meta:
        model = Prescription
        fields = ['id', 'doctor', 'doctor_email', 'patient', 'patient_email',
                  'date', 'notes', 'drugs']
        read_only_fields = ['id', 'date', 'doctor_email', 'patient_email']

    def validate(self, data):
        # Ensure date isn’t in the future (auto_now_add covers create)
        if 'date' in data and data['date'] > timezone.now():
            raise serializers.ValidationError("Date cannot be in the future.")
        return data

    def create(self, validated_data):
        drugs_data = validated_data.pop('drugs', [])
        # Enforce doctor = request.user if non-admin
        request = self.context.get('request')
        if request and request.user.role == 'doctor':
            validated_data['doctor'] = request.user
        prescription = Prescription.objects.create(**validated_data)
        for drug_data in drugs_data:
            PrescriptionDrug.objects.create(prescription=prescription, **drug_data)
        return prescription

    def update(self, instance, validated_data):
        # Allow updating notes; to update drugs, require full replace
        drugs_data = validated_data.pop('drugs', None)
        instance.notes = validated_data.get('notes', instance.notes)
        instance.save()
        if drugs_data is not None:
            # Remove old, add new
            instance.drugs.all().delete()
            for drug_data in drugs_data:
                PrescriptionDrug.objects.create(prescription=instance, **drug_data)
        return instance
