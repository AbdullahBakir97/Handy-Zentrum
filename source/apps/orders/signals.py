import uuid

from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import OrderItem, RepairOrder


@receiver(post_save, sender=OrderItem)
def update_order_total_on_item_save(sender, instance, **kwargs):
    """Update order total when an item is added or updated."""
    order = instance.order
    order.total_amount = order.calculate_total()
    order.save()


@receiver(post_delete, sender=OrderItem)
def update_order_total_on_item_delete(sender, instance, **kwargs):
    """Update order total when an item is deleted."""
    order = instance.order
    order.total_amount = order.calculate_total()
    order.save()


# @receiver(post_save, sender=Order)
# def update_order_total(sender, instance, created, **kwargs):
#     """Update total_amount after the order is saved."""
#     if created or instance.total_amount == Decimal('0.00'):
#         instance.total_amount = instance.calculate_total()
#         instance.save()


@receiver(post_save, sender=RepairOrder)
def calculate_profit_on_save(sender, instance, **kwargs):
    instance.calculate_profit()


@receiver(post_save, sender=RepairOrder)
def generate_order_code(sender, instance, created, **kwargs):
    if created and not instance.code:
        # Generate a unique code, e.g., using UUID and limiting it to 8 characters
        instance.code = str(uuid.uuid4())[:8].upper()
        instance.save()
