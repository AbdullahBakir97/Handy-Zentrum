from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import StockAdjustment, InventoryTransfer, Product, Warehouse, InventoryItem
from .services import StockAdjustmentService, NotificationService, StockService

@receiver(post_save, sender=StockAdjustment)
def handle_stock_adjustment(sender, instance, created, **kwargs):
    if created:
        StockAdjustmentService.adjust_stock(instance.inventory_item, instance.adjustment_type, instance.quantity, instance.reason, instance.performed_by)
        NotificationService.notify_stock_change(instance)

@receiver(post_save, sender=InventoryTransfer)
def handle_inventory_transfer(sender, instance, created, **kwargs):
    if created and instance.status == 'completed':
        StockAdjustmentService.adjust_stock(instance.product.inventory_records.get(location=instance.from_location), 'remove', instance.quantity, 'Transfer completed', instance.initiated_by)
        StockAdjustmentService.adjust_stock(instance.product.inventory_records.get(location=instance.to_location), 'add', instance.quantity, 'Transfer completed', instance.initiated_by)
        NotificationService.notify_transfer_completion(instance)

@receiver(post_save, sender=Product)
def notify_product_change(sender, instance, created, **kwargs):
    if created:
        NotificationService.notify_new_product(instance)
    else:
        NotificationService.notify_product_update(instance)

@receiver(post_save, sender=Warehouse)
def handle_warehouse_stock_level(sender, instance, **kwargs):
    total_stock = StockService.calculate_total_stock(instance)
    if total_stock < instance.low_stock_threshold:
        NotificationService.notify_low_stock(instance)

@receiver(post_save, sender=InventoryItem)
def notify_inventory_status_change(sender, instance, **kwargs):
    if instance.status in ['reserved', 'sold']:
        NotificationService.notify_status_change(instance)

@receiver(pre_save, sender=StockAdjustment)
def validate_stock_adjustment(sender, instance, **kwargs):
    if instance.adjustment_type == 'remove' and instance.inventory_item.quantity < instance.quantity:
        raise ValidationError("Cannot remove more items than available in stock.")
