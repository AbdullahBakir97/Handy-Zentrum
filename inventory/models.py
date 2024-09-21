from django.db import models
from django.contrib.auth.models import User
from django.forms import ValidationError


class Category(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    parent = models.ForeignKey('self', blank=True, null=True, on_delete=models.SET_NULL, related_name='child_categories')

    class Meta:
        ordering = ['name']
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

    def __str__(self):
        if self.parent:
            return f'{self.name} (Subcategory of {self.parent.name})'
        return self.name

    def clean(self):
        """Ensure a category cannot be its own parent."""
        if self.parent == self:
            raise ValidationError("A category cannot be its own parent.")
    
class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    sku = models.CharField(max_length=50, unique=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products_in_category')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        unique_together = ('name', 'sku')
        verbose_name = 'Product'
        verbose_name_plural = 'Products'

    def __str__(self):
        return f'{self.name} - SKU: {self.sku}'

    def total_stock(self):
        """Calculate total stock available for this product."""
        return self.inventory_records.aggregate(total=models.Sum('quantity'))['total'] or 0
    
class Warehouse(models.Model):
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    manager = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='warehouses_manager')

    class Meta:
        ordering = ['name']
        verbose_name = 'Warehouse'
        verbose_name_plural = 'Warehouses'

    def __str__(self):
        return f'{self.name} - {self.location}'

    def total_stock(self):
        """Returns total quantity of products in the warehouse."""
        return self.stocked_products.aggregate(total=models.Sum('quantity'))['total'] or 0
    

class InventoryItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='inventory_records')
    quantity = models.IntegerField(default=0)
    location = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name='stocked_products')
    status = models.CharField(max_length=50, choices=[('in_stock', 'In Stock'), ('reserved', 'Reserved'), ('sold', 'Sold')])
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('product', 'location')
        ordering = ['-last_updated']
        verbose_name = 'Inventory Item'
        verbose_name_plural = 'Inventory Items'

    def __str__(self):
        return f'{self.product.name} - {self.location.name} ({self.status})'

    def is_low_stock(self, threshold=10):
        """Checks if the inventory is low on stock based on a threshold."""
        return self.quantity < threshold

    def clean(self):
        """Ensure the status is valid."""
        if self.quantity == 0 and self.status != 'sold':
            raise ValidationError("An item with zero quantity should be marked as 'sold'.")
    
    def save(self, *args, **kwargs):
        """Update the last updated timestamp."""
        self.last_updated = models.DateTimeField(auto_now=True)
        super().save(*args, **kwargs)
    
class StockAdjustment(models.Model):
    inventory_item = models.ForeignKey(InventoryItem, on_delete=models.CASCADE, related_name='stock_adjustments')
    adjustment_type = models.CharField(max_length=50, choices=[('add', 'Add'), ('remove', 'Remove')])
    quantity = models.IntegerField()
    reason = models.CharField(max_length=255, blank=True, null=True)
    performed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='adjustments_performed')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Stock Adjustment'
        verbose_name_plural = 'Stock Adjustments'

    def __str__(self):
        return f'{self.adjustment_type.capitalize()} {self.quantity} of {self.inventory_item.product.name}'

    def clean(self):
        """Validates that the adjustment type and quantity are appropriate."""
        if self.adjustment_type == 'remove' and self.inventory_item.quantity < self.quantity:
            raise ValidationError("Cannot remove more items than available in stock.")
    
    
class InventoryTransfer(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='transfers_handled')
    from_location = models.ForeignKey(Warehouse, related_name='outgoing_transfers', on_delete=models.CASCADE)
    to_location = models.ForeignKey(Warehouse, related_name='incoming_transfers', on_delete=models.CASCADE)
    quantity = models.IntegerField()
    initiated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='transfers_initiated')
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, choices=[('pending', 'Pending'), ('completed', 'Completed')])

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Inventory Transfer'
        verbose_name_plural = 'Inventory Transfers'

    def __str__(self):
        return f'Transfer {self.product.name} from {self.from_location.name} to {self.to_location.name}'

    def is_transfer_possible(self):
        """Check if transfer is possible based on stock availability."""
        return self.from_location.inventory_items.filter(product=self.product).first().quantity >= self.quantity

    def clean(self):
        """Ensure stock is available before the transfer."""
        if not self.is_transfer_possible():
            raise ValidationError("Not enough stock available in the source warehouse for transfer.")
