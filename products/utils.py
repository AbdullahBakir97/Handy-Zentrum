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
        Check if the SKU is unique across all products or variants.
        :param sku: SKU to check.
        :return: Boolean indicating uniqueness.
        """
        return not Product.objects.filter(sku=sku).exists()


class BaseSKUGenerator(SKUBase):
    """
    Base SKU Generator responsible for generating base SKUs for products.
    """

    def generate_sku(self, product) -> str:
        """
        Generate SKU for a base product.
        :param product: The product instance.
        :return: Generated SKU for the base product.
        """
        return self.generate_base_sku(product)

    def generate_base_sku(self, product: Product) -> str:
        """
        Generate a base SKU using the product slug and an incremental number.
        :param product: The product instance.
        :return: SKU string.
        """
        slug_part = slugify(product.name)[:5].upper()
        # Find the latest product with the same base slug
        last_product = Product.objects.filter(sku__startswith=slug_part).order_by('sku').last()

        if last_product and last_product.sku[-3:].isdigit():
            # Increment the numeric part of the SKU
            last_number = int(last_product.sku[-3:]) + 1
        else:
            last_number = 1

        return f"{slug_part}{str(last_number).zfill(3)}"


class VariantSKUGenerator(SKUBase):
    """
    Variant SKU Generator responsible for generating SKUs for product variants.
    """

    def generate_sku(self, product: Product, variant) -> str:
        """
        Generate SKU for a product variant by appending variant-specific data to the base SKU.
        :param product: The product instance.
        :param variant: The product variant.
        :return: SKU string for the variant.
        """
        base_sku = product.sku
        color_code = (variant.color[:1] if variant.color else "0").upper()
        size_code = (variant.size[:1] if variant.size else "0").upper()
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


