from django.db import models
from django.conf import settings

class Prescription(models.Model):
    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='prescriptions_written',
        limit_choices_to={'role': 'doctor'},
        help_text='Doctor who wrote this prescription.'
    )
    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='prescriptions_received',
        limit_choices_to={'role': 'patient'},
        help_text='Patient receiving this prescription.'
    )
    date = models.DateTimeField(
        auto_now_add=True,
        help_text='Timestamp when prescription was created.'
    )
    notes = models.TextField(
        blank=True,
        null=True,
        help_text='Optional notes from the doctor.'
    )

    class Meta:
        verbose_name = 'Prescription'
        verbose_name_plural = 'Prescriptions'
        indexes = [
            models.Index(fields=['doctor', 'date']),
            models.Index(fields=['patient', 'date']),
        ]
        ordering = ['-date']

    def __str__(self):
        return f"Rx #{self.id}: {self.doctor.email} → {self.patient.email} on {self.date:%Y-%m-%d}"


class PrescriptionDrug(models.Model):
    prescription = models.ForeignKey(
        Prescription,
        on_delete=models.CASCADE,
        related_name='drugs',
        help_text='Prescription to which this drug belongs.'
    )
    drug = models.ForeignKey(
        'inventory.Drug',
        on_delete=models.PROTECT,
        related_name='prescription_drugs',
        help_text='Drug being prescribed.'
    )
    dosage = models.CharField(
        max_length=100,
        help_text='Dosage instructions, e.g. "500mg twice daily".'
    )
    quantity = models.PositiveIntegerField(
        help_text='Total quantity of this drug prescribed.'
    )

    class Meta:
        verbose_name = 'Prescription Drug'
        verbose_name_plural = 'Prescription Drugs'
        unique_together = [('prescription', 'drug')]
        indexes = [
            models.Index(fields=['drug']),
        ]

    def __str__(self):
        return f"{self.drug.name}: {self.dosage} x {self.quantity}"
