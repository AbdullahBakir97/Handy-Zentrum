from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import RepairOrder

@receiver(post_save, sender=RepairOrder)
def calculate_profit_on_save(sender, instance, **kwargs):
    instance.calculate_profit()