from django.db import models
from django.conf import settings

class Appointment(models.Model):
    STATUS_SCHEDULED = 'scheduled'
    STATUS_COMPLETED = 'completed'
    STATUS_CANCELLED = 'cancelled'
    STATUS_CHOICES = [
        (STATUS_SCHEDULED, 'Scheduled'),
        (STATUS_COMPLETED, 'Completed'),
        (STATUS_CANCELLED, 'Cancelled'),
    ]

    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='appointments_as_patient',
        limit_choices_to={'role': 'patient'},
        help_text='The patient who booked this appointment.'
    )
    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='appointments_as_doctor',
        limit_choices_to={'role': 'doctor'},
        help_text='The doctor assigned to this appointment.'
    )
    datetime = models.DateTimeField(
        help_text='Date and time of the appointment.'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_SCHEDULED,
        help_text='Current status of the appointment.'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Appointment'
        verbose_name_plural = 'Appointments'
        indexes = [
            models.Index(fields=['doctor', 'datetime']),
            models.Index(fields=['patient', 'datetime']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['doctor', 'datetime'],
                name='unique_doctor_datetime'
            )
        ]

    def __str__(self):
        return f"{self.patient.email} with {self.doctor.email} at {self.datetime}"
