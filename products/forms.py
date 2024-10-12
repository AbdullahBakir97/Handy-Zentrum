from .models import Product
from django import forms


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'category', 'base_price', 'slug']