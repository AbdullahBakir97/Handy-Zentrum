from django.db import models
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
    