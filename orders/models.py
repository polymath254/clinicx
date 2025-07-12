from django.db import models
from django.conf import settings
from django.db import transaction
from django.db.models import F
from django.core.exceptions import ValidationError
from inventory.models import Drug
from prescriptions.models import Prescription, PrescriptionDrug

class Order(models.Model):
    STATUS_PENDING    = 'pending'
    STATUS_DISPENSED  = 'dispensed'
    STATUS_CANCELLED  = 'cancelled'
    STATUS_CHOICES    = [
        (STATUS_PENDING,   'Pending'),
        (STATUS_DISPENSED, 'Dispensed'),
        (STATUS_CANCELLED, 'Cancelled'),
    ]

    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='orders',
        limit_choices_to={'role': 'patient'},
        help_text='Patient placing the order.'
    )
    prescription = models.ForeignKey(
        Prescription,
        on_delete=models.CASCADE,
        related_name='orders',
        help_text='Prescription this order fulfills.'
    )
    drug = models.ForeignKey(
        Drug,
        on_delete=models.PROTECT,
        related_name='orders',
        help_text='Drug being ordered.'
    )
    quantity = models.PositiveIntegerField(help_text='Number of units to dispense.')
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
        help_text='Order lifecycle status.'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'
        indexes = [
            models.Index(fields=['patient']),
            models.Index(fields=['prescription']),
            models.Index(fields=['drug']),
        ]

    def __str__(self):
        return f"Order#{self.id} ({self.patient.email} → {self.drug.name})"

    def clean(self):
        # Ensure drug is one of the prescription's drugs
        if not PrescriptionDrug.objects.filter(
            prescription=self.prescription, drug=self.drug
        ).exists():
            raise ValidationError("This drug is not part of the given prescription.")

        # Ensure quantity does not exceed prescribed amount
        pd = PrescriptionDrug.objects.get(prescription=self.prescription, drug=self.drug)
        if self.quantity > pd.quantity:
            raise ValidationError("Quantity exceeds the prescribed amount.")

    def save(self, *args, **kwargs):
        # Validate relation integrity
        self.clean()
        super().save(*args, **kwargs)

    @transaction.atomic
    def process(self):
        """
        Atomically attempt to dispense:
        - Lock the drug row
        - If enough stock: deduct & mark dispensed
        - Else: leave pending & trigger reorder
        """
        drug = Drug.objects.select_for_update().get(pk=self.drug.pk)
        if drug.quantity >= self.quantity:
            drug.quantity = F('quantity') - self.quantity
            drug.save()
            # refresh to compute needs_reorder and trigger signals
            drug.refresh_from_db()
            self.status = self.STATUS_DISPENSED
            self.save()
        else:
            # not enough stock: trigger reorder on Drug signal
            drug.check_and_create_purchase_order()
            self.status = self.STATUS_PENDING
            self.save()

