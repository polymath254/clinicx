from datetime import date
from rest_framework import serializers
from .models import PatientProfile

class PatientProfileSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        source='user.email',
        read_only=True,
        help_text="The patient's login email (read-only)."
    )
    username = serializers.CharField(
        source='user.username',
        read_only=True
    )
    role = serializers.CharField(
        source='user.role',
        read_only=True
    )

    class Meta:
        model = PatientProfile
        fields = [
            'id', 'email', 'username', 'role',
            'allergies', 'date_of_birth', 'bio'
        ]
        read_only_fields = ('id', 'email', 'username', 'role')
        extra_kwargs = {
            'bio': {
                'allow_blank': True,
                'max_length': 2000,
                'help_text': 'Optional patient bio (max 2000 chars).'
            },
            'allergies': {
                'allow_blank': True,
                'max_length': 1000,
                'help_text': 'List patient allergies, comma-separated.'
            },
        }

    def validate_date_of_birth(self, value):
        """Ensure date_of_birth is not in the future."""
        if value and value > date.today():
            raise serializers.ValidationError("Date of birth cannot be in the future.")
        return value

    def validate_allergies(self, value):
        """Trim whitespace and enforce a sensible length."""
        cleaned = value.strip()
        if len(cleaned) > 1000:
            raise serializers.ValidationError("Allergies description too long (max 1000 chars).")
        return cleaned

    def update(self, instance, validated_data):
        """
        Override update to hook into audit logging or
        handle nested user updates in the future.
        """
        # Update profile fields
        for attr, val in validated_data.items():
            setattr(instance, attr, val)
        instance.save()

        # Example audit hook (if you had an AuditLog model)
        # AuditLog.log(
        #     user=self.context['request'].user,
        #     action='updated patient profile',
        #     target=instance
        # )

        return instance

