from rest_framework import serializers
from .models import DoctorProfile

class DoctorProfileSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source='user.email', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    role = serializers.CharField(source='user.role', read_only=True)

    class Meta:
        model = DoctorProfile
        fields = [
            'id', 'email', 'username', 'role',
            'specialty', 'schedule'
        ]
        read_only_fields = ('id', 'email', 'username', 'role')
        extra_kwargs = {
            'specialty': {
                'help_text': 'Doctor specialty (max 100 chars)',
                'max_length': 100,
            },
            'schedule': {
                'help_text': 'Availability JSON structure',
            },
        }

    def validate_specialty(self, value):
        if not value.strip():
            raise serializers.ValidationError("Specialty cannot be empty.")
        return value

    def validate_schedule(self, value):
        if value is None:
            return value
        if not isinstance(value, (dict, list)):
            raise serializers.ValidationError("Schedule must be a JSON object or list.")
        return value

    def update(self, instance, validated_data):
        instance.specialty = validated_data.get('specialty', instance.specialty)
        instance.schedule = validated_data.get('schedule', instance.schedule)
        instance.save()
        # TODO: insert audit log here if desired
        return instance
