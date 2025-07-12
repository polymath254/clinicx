from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Drug

@receiver(post_save, sender=Drug)
def auto_reorder(sender, instance, created, **kwargs):
    instance.check_and_create_purchase_order()
