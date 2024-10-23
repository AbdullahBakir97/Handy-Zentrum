from django import forms
from django.utils.text import slugify

from .models import Brand, Category, Product, ProductImages, ProductVariant


# Brand Form
class BrandForm(forms.ModelForm):
    class Meta:
        model = Brand
        fields = ["name", "description", "slug", "image"]

    def clean_slug(self):
        slug = self.cleaned_data.get("slug")
        if not slug:
            slug = slugify(self.cleaned_data.get("name"))
        return slug


# Category Form
class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["name", "description", "slug", "parent", "image"]

    def clean(self):
        cleaned_data = super().clean()
        parent = cleaned_data.get("parent")

        if parent == self.instance:
            raise forms.ValidationError("A category cannot be its own parent.")
        return cleaned_data

    def clean_slug(self):
        slug = self.cleaned_data.get("slug")
        if not slug:
            slug = slugify(self.cleaned_data.get("name"))
        return slug


# Product Form
class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            "name",
            "subtitle",
            "description",
            "category",
            "brand",
            "base_price",
            "flag",
            "slug",
            "sku",
            "tags",
            "image",
        ]

    def clean_sku(self):
        sku = self.cleaned_data.get("sku")
        if not sku:
            from .utils import BaseSKUGenerator

            sku_generator = BaseSKUGenerator()
            sku = sku_generator.generate_sku(self.instance)
        return sku

    def clean_slug(self):
        slug = self.cleaned_data.get("slug")
        if not slug:
            slug = slugify(self.cleaned_data.get("name"))
        return slug


# Product Images Form
class ProductImagesForm(forms.ModelForm):
    class Meta:
        model = ProductImages
        fields = ["product", "image"]


# Product Variant Form
class ProductVariantForm(forms.ModelForm):
    class Meta:
        model = ProductVariant
        fields = [
            "product",
            "color",
            "size",
            "sku",
            "price",
            "weight",
            "dimensions",
            "stock",
            "variant_group",
        ]

    def clean(self):
        cleaned_data = super().clean()
        product = cleaned_data.get("product")
        color = cleaned_data.get("color")
        size = cleaned_data.get("size")

        # Ensure uniqueness of color and size combination per product
        if ProductVariant.objects.filter(
            product=product, color=color, size=size
        ).exists():
            raise forms.ValidationError(
                "This combination of color and size already exists for the selected product."
            )
        return cleaned_data

    def clean_sku(self):
        sku = self.cleaned_data.get("sku")
        if not sku:
            product = self.cleaned_data.get("product")
            color = self.cleaned_data.get("color")
            size = self.cleaned_data.get("size")
            sku = f"{product.sku}-{color[:1].upper()}-{size[:1].upper()}"
        return sku
