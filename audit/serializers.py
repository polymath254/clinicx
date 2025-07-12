from rest_framework import serializers
from .models import AuditLog

class AuditLogSerializer(serializers.ModelSerializer):
    user_email       = serializers.EmailField(source='user.email', read_only=True)
    content_type     = serializers.CharField(source='content_type.model', read_only=True)

    class Meta:
        model = AuditLog
        fields = [
            'id', 'timestamp', 'user', 'user_email',
            'action', 'content_type', 'object_id', 'details'
        ]
        read_only_fields = fields
