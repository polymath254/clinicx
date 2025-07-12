from rest_framework import serializers
from .models import NotificationLog

class NotificationLogSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = NotificationLog
        fields = [
            'id', 'notification_type', 'status',
            'recipient', 'subject', 'message',
            'response', 'error_message',
            'user', 'user_email',
            'created_at', 'updated_at',
        ]
        read_only_fields = fields  # logs are read-only via API
