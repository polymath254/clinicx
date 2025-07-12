from django.db import models
from django.conf import settings

class DoctorProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='doctor_profile'
    )
    specialty = models.CharField(
        max_length=100,
        help_text='Doctor specialty, e.g. Cardiology'
    )
    schedule = models.JSONField(
        blank=True,
        null=True,
        help_text='Weekly availability JSON, e.g. {"monday": ["09:00-12:00", "14:00-17:00"], …}'
    )

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.email} — {self.specialty}"

    class Meta:
        verbose_name = 'Doctor Profile'
        verbose_name_plural = 'Doctor Profiles'
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['specialty']),
        ]

    def is_assigned_to(self, doctor_user):
        """
        Stub: replace with real doctor–patient assignment logic.
        e.g. return self.assignment_set.filter(doctor=doctor_user).exists()
        """
        return False
