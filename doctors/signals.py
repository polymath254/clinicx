from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import DoctorProfile

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_doctor_profile(sender, instance, created, **kwargs):
    if created and instance.role == 'doctor':
        DoctorProfile.objects.get_or_create(user=instance)
