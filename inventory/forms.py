from django import forms
from .models import Product, StockAdjustment, InventoryTransfer

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'sku', 'category', 'price']

class StockAdjustmentForm(forms.ModelForm):
    class Meta:
        model = StockAdjustment
        fields = ['inventory_item', 'adjustment_type', 'quantity', 'reason']

class InventoryTransferForm(forms.ModelForm):
    class Meta:
        model = InventoryTransfer
        fields = ['product', 'from_location', 'to_location', 'quantity']