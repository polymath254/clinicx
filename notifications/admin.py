from django.contrib import admin
from .models import NotificationLog

@admin.register(NotificationLog)
class NotificationLogAdmin(admin.ModelAdmin):
    list_display  = ('notification_type', 'recipient', 'status', 'user', 'created_at')
    list_filter   = ('notification_type', 'status', 'created_at')
    search_fields = ('recipient', 'subject', 'message', 'error_message')
    readonly_fields = [f.name for f in NotificationLog._meta.fields]
