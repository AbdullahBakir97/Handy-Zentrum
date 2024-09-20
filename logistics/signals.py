from django.db.models.signals import post_save
from django.dispatch import receiver
from .utils import adjust_stock_level
from .models import Shipment, ReturnShipment, LogisticsInteraction
from inventory.models import InventoryItem

@receiver(post_save, sender=Shipment)
def handle_shipment_delivered(sender, instance, **kwargs):
    if instance.status == 'delivered':
        adjust_stock_level(instance.product.inventory_records.first(), instance.quantity, 'remove')
        
        
@receiver(post_save, sender=ReturnShipment)
def handle_return_received(sender, instance, **kwargs):
    if instance.status == 'received':
        # Notify finance department to process refund
        pass
    
@receiver(post_save, sender=Shipment)
def handle_shipment_status_change(sender, instance, created, **kwargs):
    if not created:
        if instance.status == 'delivered':
            # Automatically log a 'delivered' logistics interaction
            LogisticsInteraction.objects.create(
                shipment=instance,
                interaction_type='delivered',
                notes='Shipment delivered successfully.'
            )
            
            
@receiver(post_save, sender=Shipment)
def adjust_stock_on_shipment(sender, instance, created, **kwargs):
    if created and instance.status == 'pending':
        # Deduct stock from warehouse upon shipment creation
        inventory_item = InventoryItem.objects.get(
            product=instance.product,
            location=instance.origin
        )
        inventory_item.quantity -= instance.quantity
        inventory_item.save()