# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from .models import StockAdjustment, InventoryTransfer
# from .services import StockAdjustmentService, NotificationService

# @receiver(post_save, sender=StockAdjustment)
# def handle_stock_adjustment(sender, instance, created, **kwargs):
#     if created:
#         StockAdjustmentService.adjust_stock(instance)
#         # Optionally notify managers or users
#         NotificationService.notify_stock_change(instance)

# @receiver(post_save, sender=InventoryTransfer)
# def handle_inventory_transfer(sender, instance, created, **kwargs):
#     if created and instance.status == 'completed':
#         # Automatically adjust stock after transfer completion
#         StockAdjustmentService.handle_transfer_completion(instance)
#         NotificationService.notify_transfer_completion(instance)