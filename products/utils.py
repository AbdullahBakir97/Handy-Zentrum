import random
import string
from django.db import models
from django.core.exceptions import ValidationError
from .models import Product, ProductVariant
from django.utils.text import slugify



class SKUBase:
    """
    Interface for SKU-related functionality. Provides methods for SKU generation and validation.
    """

    def generate_sku(self, product, variant_data=None):
        raise NotImplementedError("This method should be overridden by subclasses.")

    def is_sku_unique(self, sku: str) -> bool:
        """
        Check if the SKU is unique across all product variants.
        :param sku: SKU to check.
        :return: Boolean indicating uniqueness.
        """
        return not Product.objects.filter(sku=sku).exists()


class BaseSKUGenerator(SKUBase):
    """
    Base SKU Generator responsible for generating base SKUs for products.
    """

    def generate_sku(self, product, variant_data=None) -> str:
        """
        Generate SKU for a base product.
        :param product: The product instance.
        :return: Generated SKU for the base product.
        """
        return self.generate_base_sku(product.name)

    def generate_base_sku(self, product_name: str, length: int = 8) -> str:
        """
        Generate a base SKU using the product name and a random string.
        :param product_name: The name of the product.
        :param length: The length of the random part of the SKU.
        :return: SKU string.
        """
        base_slug = slugify(product_name)
        random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
        return f"{base_slug[:5].upper()}-{random_str}"


class VariantSKUGenerator(BaseSKUGenerator):
    """
    Variant SKU Generator responsible for generating SKUs for product variants.
    """

    def generate_sku(self, product, variant_data=None) -> str:
        """
        Generate SKU for a product variant.
        :param product: The product instance.
        :param variant_data: Optional dictionary containing variant fields.
        :return: Generated SKU for the variant.
        """
        base_sku = self.generate_base_sku(product.name)
        return self.generate_variant_sku(base_sku, variant_data)

    def generate_variant_sku(self, base_sku: str, variant: ProductVariant) -> str:
        """
        Generate a variant SKU by appending variant-specific data to the base SKU.
        :param base_sku: The base SKU of the product.
        :param variant: The product variant.
        :return: SKU string for the variant.
        """
        color_code = (variant.color[:3] if variant.color else "00").upper()
        size_code = (variant.size[:3] if variant.size else "00").upper()
        return f"{base_sku}-{color_code}-{size_code}"


class ProductValidation:
    """
    Handles product and variant validation. Adheres to SRP by focusing only on validation logic.
    """

    @staticmethod
    def validate_variant_uniqueness(product: Product, variant_data: dict):
        """
        Ensure that the combination of color and size is unique for a product.
        :param product: The product instance.
        :param variant_data: Dictionary containing variant fields (color, size).
        :raise: ValidationError if a duplicate combination is found.
        """
        color = variant_data.get('color')
        size = variant_data.get('size')
        exists = ProductVariant.objects.filter(
            product=product, color=color, size=size
        ).exists()
        if exists:
            raise ValidationError(f"A variant with color {color} and size {size} already exists for this product.")
    
    @staticmethod
    def validate_stock_level(variant: ProductVariant, requested_quantity: int):
        """
        Ensure that the requested stock is available.
        :param variant: The product variant.
        :param requested_quantity: The quantity requested.
        :raise: ValidationError if stock is insufficient.
        """
        if variant.stock < requested_quantity:
            raise ValidationError("Not enough stock available.")


