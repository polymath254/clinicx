from django.db import models
from django.conf import settings

class NotificationLog(models.Model):
    TYPE_EMAIL = 'email'
    TYPE_SMS   = 'sms'
    TYPE_CHOICES = [
        (TYPE_EMAIL, 'Email'),
        (TYPE_SMS,   'SMS'),
    ]

    STATUS_PENDING = 'pending'
    STATUS_SENT    = 'sent'
    STATUS_FAILED  = 'failed'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_SENT,    'Sent'),
        (STATUS_FAILED,  'Failed'),
    ]

    user            = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
                                        on_delete=models.SET_NULL,
                                        help_text="User who triggered this notification, if any.")
    notification_type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    recipient       = models.CharField(max_length=255,
                                       help_text="Email address or phone number.")
    subject         = models.CharField(max_length=255, blank=True, null=True)
    message         = models.TextField()
    status          = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_PENDING)
    response        = models.JSONField(blank=True, null=True,
                                       help_text="Provider response payload, if any.")
    error_message   = models.TextField(blank=True, null=True)
    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Notification Log'
        verbose_name_plural = 'Notification Logs'
        indexes = [
            models.Index(fields=['notification_type']),
            models.Index(fields=['status']),
            models.Index(fields=['recipient']),
        ]

    def __str__(self):
        return f"{self.get_notification_type_display()} to {self.recipient} [{self.status}]"
