
from django.db import models
from django.conf import settings

class PatientProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='patient_profile'
    )
    allergies = models.TextField(blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    bio = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.email} Profile"

    class Meta:
        verbose_name = 'Patient Profile'
        verbose_name_plural = 'Patient Profiles'
        indexes = [
            models.Index(fields=['user']),
        ]

    def is_assigned_to(self, doctor_user):
        """
        Stub for doctor–patient assignment check.
        Replace with real logic, e.g.:
        return self.assignment_set.filter(doctor=doctor_user).exists()
        """
        return False

        

