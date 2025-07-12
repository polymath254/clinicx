from django.db import models
from django.conf import settings
from django.utils import timezone
from decimal import Decimal

class Invoice(models.Model):
    STATUS_PENDING   = 'pending'
    STATUS_PAID      = 'paid'
    STATUS_CANCELLED = 'cancelled'
    STATUS_CHOICES   = [
        (STATUS_PENDING,   'Pending'),
        (STATUS_PAID,      'Paid'),
        (STATUS_CANCELLED, 'Cancelled'),
    ]

    patient     = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='invoices',
        limit_choices_to={'role': 'patient'},
    )
    amount      = models.DecimalField(max_digits=10, decimal_places=2)
    status      = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
    )
    created_at  = models.DateTimeField(auto_now_add=True)
    due_date    = models.DateTimeField(blank=True, null=True)

    class Meta:
        indexes = [
            models.Index(fields=['patient', 'status']),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f"Invoice#{self.id} [{self.status}] – {self.patient.email}"

    def mark_paid(self):
        self.status = self.STATUS_PAID
        self.save()

    def mark_cancelled(self):
        self.status = self.STATUS_CANCELLED
        self.save()


class Payment(models.Model):
    STATUS_INITIATED = 'initiated'
    STATUS_SUCCESS   = 'success'
    STATUS_FAILED    = 'failed'
    STATUS_CHOICES   = [
        (STATUS_INITIATED, 'Initiated'),
        (STATUS_SUCCESS,   'Success'),
        (STATUS_FAILED,    'Failed'),
    ]

    invoice               = models.OneToOneField(Invoice, on_delete=models.CASCADE, related_name='payment')
    amount                = models.DecimalField(max_digits=10, decimal_places=2)
    mpesa_checkout_request_id = models.CharField(max_length=64, blank=True, null=True)
    mpesa_receipt_number     = models.CharField(max_length=64, blank=True, null=True)
    status                   = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_INITIATED,
    )
    created_at               = models.DateTimeField(auto_now_add=True)
    updated_at               = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"Payment#{self.id} for Invoice#{self.invoice.id} [{self.status}]"
