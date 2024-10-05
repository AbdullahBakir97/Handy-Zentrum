from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import RepairOrder
import uuid

@receiver(post_save, sender=RepairOrder)
def calculate_profit_on_save(sender, instance, **kwargs):
    instance.calculate_profit()
    
@receiver(post_save, sender=RepairOrder)
def generate_order_code(sender, instance, created, **kwargs):
    if created and not instance.code:
        # Generate a unique code, e.g., using UUID and limiting it to 8 characters
        instance.code = str(uuid.uuid4())[:8].upper()
        instance.save()