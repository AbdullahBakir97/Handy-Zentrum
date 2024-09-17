from django.db import models
from django.contrib.auth.models import User


class Category(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    parent = models.ForeignKey('self', blank=True, null=True, on_delete=models.SET_NULL, related_name='child_categories')

    def __str__(self):
        return self.name
    
class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    sku = models.CharField(max_length=50, unique=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products_in_category')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
class Warehouse(models.Model):
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    manager = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='warehouses_manager')

    def __str__(self):
        return self.name
    

class InventoryItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='inventory_records')
    quantity = models.IntegerField(default=0)
    location = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name='stocked_products')
    status = models.CharField(max_length=50, choices=[('in_stock', 'In Stock'), ('reserved', 'Reserved'), ('sold', 'Sold')])
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.product.name} - {self.location}'
    

    
    
class StockAdjustment(models.Model):
    inventory_item = models.ForeignKey(InventoryItem, on_delete=models.CASCADE, related_name='stock_adjustments')
    adjustment_type = models.CharField(max_length=50, choices=[('add', 'Add'), ('remove', 'Remove')])
    quantity = models.IntegerField()
    reason = models.CharField(max_length=255, blank=True, null=True)
    performed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='adjustments_performed')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.adjustment_type} {self.quantity} of {self.inventory_item}'
    
    
class InventoryTransfer(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='transfers_handled')
    from_location = models.ForeignKey(Warehouse, related_name='outgoing_transfers', on_delete=models.CASCADE)
    to_location = models.ForeignKey(Warehouse, related_name='incoming_transfers', on_delete=models.CASCADE)
    quantity = models.IntegerField()
    initiated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='transfers_initiated')
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, choices=[('pending', 'Pending'), ('completed', 'Completed')])

    def __str__(self):
        return f'Transfer of {self.product.name} from {self.from_location} to {self.to_location}'