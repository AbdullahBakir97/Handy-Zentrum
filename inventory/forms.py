from django import forms
from .models import StockAdjustment, InventoryTransfer


class StockAdjustmentForm(forms.ModelForm):
    class Meta:
        model = StockAdjustment
        fields = ['inventory_item', 'adjustment_type', 'quantity', 'reason']

class InventoryTransferForm(forms.ModelForm):
    class Meta:
        model = InventoryTransfer
        fields = ['product', 'from_location', 'to_location', 'quantity']