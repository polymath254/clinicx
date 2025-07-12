import sys
import json
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from django.forms.models import model_to_dict
from django.utils import timezone
from .models import AuditLog
from django.core.signals import request_finished
from django.contrib.auth import get_user_model
from threading import local

_user = local()

def get_current_user():
    return getattr(_user, 'value', None)

class RequestMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        _user.value = request.user if request.user.is_authenticated else None
        response = self.get_response(request)
        return response

@receiver(post_save)
def audit_on_save(sender, instance, created, **kwargs):
    if sender.__name__ == 'AuditLog':
        return
    if 'makemigrations' in sys.argv or 'migrate' in sys.argv:
        return
    action = AuditLog.ACTION_CREATE if created else AuditLog.ACTION_UPDATE
    user = get_current_user()
    ct = ContentType.objects.get_for_model(sender)
    try:
        details = model_to_dict(instance)
    except Exception:
        details = {'__repr__': str(instance)}
    AuditLog.objects.create(
        user=user,
        action=action,
        content_type=ct,
        object_id=str(instance.pk),
        details=details,
        timestamp=timezone.now()
    )

@receiver(post_delete)
def audit_on_delete(sender, instance, **kwargs):
    if sender.__name__ == 'AuditLog':
        return
    if 'makemigrations' in sys.argv or 'migrate' in sys.argv:
        return
    user = get_current_user()
    ct = ContentType.objects.get_for_model(sender)
    AuditLog.objects.create(
        user=user,
        action=AuditLog.ACTION_DELETE,
        content_type=ct,
        object_id=str(instance.pk),
        details={'__repr__': str(instance)},
        timestamp=timezone.now()
    )

