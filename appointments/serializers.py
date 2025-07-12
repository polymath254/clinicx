from rest_framework import serializers
from django.utils import timezone
from .models import Appointment

class AppointmentSerializer(serializers.ModelSerializer):
    patient_email = serializers.EmailField(
        source='patient.email',
        read_only=True
    )
    doctor_email = serializers.EmailField(
        source='doctor.email',
        read_only=True
    )

    class Meta:
        model = Appointment
        fields = [
            'id',
            'patient',
            'patient_email',
            'doctor',
            'doctor_email',
            'datetime',
            'status',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'patient_email',
            'doctor_email',
            'created_at',
            'updated_at',
        ]

    def validate_datetime(self, value):
        if value < timezone.now():
            raise serializers.ValidationError("Appointment datetime must be in the future.")
        return value

    def validate(self, data):
        doctor = data.get('doctor', getattr(self.instance, 'doctor', None))
        appt_time = data.get('datetime', getattr(self.instance, 'datetime', None))
        # Check for existing at same time
        conflict_qs = Appointment.objects.filter(
            doctor=doctor,
            datetime=appt_time
        )
        if self.instance:
            conflict_qs = conflict_qs.exclude(pk=self.instance.pk)
        if conflict_qs.exists():
            raise serializers.ValidationError("Doctor is already booked at this time.")
        return data

    def create(self, validated_data):
        # Enforce patient = request.user for non-admin
        request = self.context.get('request')
        if request and request.user.role == 'patient':
            validated_data['patient'] = request.user
        return super().create(validated_data)
