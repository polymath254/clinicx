from django.db import models
from django.utils import timezone

class Supplier(models.Model):
    name       = models.CharField(max_length=255)
    email      = models.EmailField()
    phone      = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Supplier'
        verbose_name_plural = 'Suppliers'
        indexes = [models.Index(fields=['name'])]

    def __str__(self):
        return self.name


class Drug(models.Model):
    name              = models.CharField(max_length=255, unique=True)
    description       = models.TextField(blank=True, null=True)
    price             = models.DecimalField(max_digits=10, decimal_places=2)
    quantity          = models.PositiveIntegerField()
    reorder_threshold = models.PositiveIntegerField(default=0)
    supplier          = models.ForeignKey(Supplier, on_delete=models.PROTECT, related_name='drugs')
    created_at        = models.DateTimeField(auto_now_add=True)
    updated_at        = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Drug'
        verbose_name_plural = 'Drugs'
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['supplier']),
        ]

    def __str__(self):
        return self.name

    @property
    def needs_reorder(self):
        return self.quantity <= self.reorder_threshold

    def check_and_create_purchase_order(self):
        from .models import PurchaseOrder
        if self.needs_reorder:
            # Avoid duplicate pending orders
            if not PurchaseOrder.objects.filter(drug=self, status=PurchaseOrder.STATUS_PENDING).exists():
                PurchaseOrder.objects.create(
                    supplier=self.supplier,
                    drug=self,
                    quantity=self.reorder_threshold * 2,
                    status=PurchaseOrder.STATUS_PENDING,
                )


class PurchaseOrder(models.Model):
    STATUS_PENDING   = 'pending'
    STATUS_DELIVERED = 'delivered'
    STATUS_CANCELLED = 'cancelled'
    STATUS_CHOICES   = [
        (STATUS_PENDING,   'Pending'),
        (STATUS_DELIVERED, 'Delivered'),
        (STATUS_CANCELLED, 'Cancelled'),
    ]

    supplier    = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='purchase_orders')
    drug        = models.ForeignKey(Drug,     on_delete=models.CASCADE, related_name='purchase_orders')
    quantity    = models.PositiveIntegerField()
    status      = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    created_at  = models.DateTimeField(auto_now_add=True)
    delivered_at= models.DateTimeField(blank=True, null=True)

    class Meta:
        verbose_name = 'Purchase Order'
        verbose_name_plural = 'Purchase Orders'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['supplier']),
            models.Index(fields=['drug']),
        ]
        constraints = [
            models.CheckConstraint(check=models.Q(quantity__gt=0), name='quantity_positive'),
        ]

    def __str__(self):
        return f"PO#{self.id} {self.drug.name} x{self.quantity} → {self.supplier.name}"

    def mark_delivered(self):
        self.status      = self.STATUS_DELIVERED
        self.delivered_at= timezone.now()
        self.save()

