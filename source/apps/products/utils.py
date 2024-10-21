import csv
import logging

from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.db import models
from django.utils.text import slugify

from source.apps.inventory.models import Warehouse

from .models import Product, ProductVariant

logger = logging.getLogger(__name__)


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
        last_product = (
            Product.objects.filter(sku__startswith=slug_part).order_by("sku").last()
        )

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

    @staticmethod
    def generate_sku(product: Product, variant) -> str:
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
        color = variant_data.get("color")
        size = variant_data.get("size")
        exists = ProductVariant.objects.filter(
            product=product, color=color, size=size
        ).exists()
        if exists:
            raise ValidationError(
                f"A variant with color {color} and size {size} already exists for this product."
            )

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


def log_bulk_variant_change(variants, change_type, user):
    """
    Log bulk changes made to product variants.
    """
    for variant in variants:
        logger.info(
            f"User {user} made a {change_type} change to variant {variant.sku} (Product: {variant.product.name}): "
            f"Price: {variant.price}, Stock: {variant.stock}, Color: {variant.color}, Size: {variant.size}"
        )


def calculate_variant_price(product, variant_price=None):
    """
    Calculate the final price of a product variant. If a variant price
    is given, use that. Otherwise, fall back to the product's base price.
    """
    return variant_price or product.base_price


def calculate_product_price_range(product):
    """
    Calculate the minimum and maximum prices for a product based on its variants.
    """
    variants = ProductVariant.objects.filter(product=product)
    min_price = variants.aggregate(models.Min("price"))["price__min"]
    max_price = variants.aggregate(models.Max("price"))["price__max"]
    return min_price, max_price


def create_product_variants_in_bulk(product, variants_data):
    """
    Create multiple product variants in bulk.
    """
    variants = [
        ProductVariant(
            product=product,
            sku=VariantSKUGenerator.generate_sku(product, variant),
            color=variant["color"],
            size=variant["size"],
            price=calculate_variant_price(product, variant.get("price")),
            stock=variant.get("stock", 0),
        )
        for variant in variants_data
    ]
    ProductVariant.objects.bulk_create(variants)
    return variants


def bulk_update_variant_prices(variants, new_price, user):
    """
    Update the price for multiple product variants in bulk.
    """
    for variant in variants:
        variant.price = new_price
        variant.save()
        # TODO Create log_variant_change function
        # log_variant_change(variant, "bulk price update", user)


def bulk_update_variant_stock(variants, new_stock, user):
    """
    Update the stock for multiple product variants in bulk.
    """
    for variant in variants:
        variant.stock = new_stock
        variant.save()
        # TODO Create log_variant_change function
        # log_variant_change(variant, "bulk stock update", user)


CACHE_TIMEOUT = 60 * 15  # Cache for 15 minutes


def get_cached_product_details(product_id):
    """
    Cache product details including variants and price range.
    """
    cache_key = f"product_{product_id}_details"
    product_data = cache.get(cache_key)

    if not product_data:
        product = Product.objects.get(id=product_id)
        variants = ProductVariant.objects.filter(product=product)
        min_price, max_price = calculate_product_price_range(product)

        product_data = {
            "product": product,
            "variants": list(variants),
            "price_range": {"min": min_price, "max": max_price},
        }
        cache.set(cache_key, product_data, CACHE_TIMEOUT)

    return product_data


def invalidate_product_cache(product_id):
    """
    Invalidate the cache for a specific product when its details change.
    """
    cache_key = f"product_{product_id}_details"
    cache.delete(cache_key)


CACHE_VARIANT_TIMEOUT = 3600  # Cache for 1 hour


def cache_variant(variant):
    """
    Cache a product variant's data for faster access.
    """
    cache.set(f"variant_{variant.id}", variant, timeout=CACHE_VARIANT_TIMEOUT)


def get_cached_variant(variant_id):
    """
    Retrieve a cached product variant or fetch it from the database.
    """
    variant = cache.get(f"variant_{variant_id}")
    if not variant:
        variant = ProductVariant.objects.get(id=variant_id)
        cache_variant(variant)
    return variant


def invalidate_variant_cache(variant_id):
    """
    Invalidate the cache for a specific product variant.
    """
    cache.delete(f"variant_{variant_id}")


def send_stock_alert(variant):
    """
    Send an email alert when stock falls below a threshold.
    """
    if variant.stock < 5:
        send_mail(
            "Low Stock Alert",
            f"The variant {variant.sku} is low in stock!",
            "from@example.com",
            ["admin@example.com"],
        )


def send_price_change_alert(variant, old_price, new_price):
    """
    Send an email notification when a product variant's price changes.
    """
    if old_price != new_price:
        send_mail(
            "Price Change Alert",
            f"The price for variant {variant.sku} has changed from {old_price} to {new_price}.",
            "from@example.com",
            ["admin@example.com"],
        )


def send_bulk_stock_alert(product):
    """
    Send a bulk notification when any of the product variants are low in stock.
    """
    low_stock_variants = product.variants.filter(stock__lt=5)
    if low_stock_variants.exists():
        send_mail(
            "Bulk Low Stock Alert",
            f"The following variants of product {product.name} are low in stock: {[v.sku for v in low_stock_variants]}",
            "from@example.com",
            ["admin@example.com"],
        )


def update_variant_stock(variant, new_stock):
    """
    Update the stock for a product variant and send a notification if the stock is low.
    """
    variant.stock = new_stock
    variant.save()
    if variant.stock < 5:
        send_stock_alert(variant)


def update_variant_price(variant, new_price):
    """
    Update the price for a product variant and send a notification if the price changes.
    """
    old_price = variant.price
    variant.price = new_price
    variant.save()
    send_price_change_alert(variant, old_price, new_price)


def sync_variant_across_warehouses(variant, quantity, warehouses):
    """
    Sync product variant stock across multiple warehouses.
    """
    for warehouse in warehouses:
        # Logic for updating stock in each warehouse
        variant.stock = quantity
        variant.warehouse = warehouse
        variant.save()


def generate_warehouse_stock_report(product_id):
    """
    Generate a report of stock levels for a product across multiple warehouses.
    """
    variants = ProductVariant.objects.filter(product_id=product_id)
    report = {}
    for variant in variants:
        report.setdefault(variant.warehouse.name, []).append(
            {
                "variant": variant.sku,
                "stock": variant.stock,
            }
        )
    return report


def export_product_variants_to_csv(product_id):
    """
    Export product variants for a specific product to CSV.
    """
    product = Product.objects.get(id=product_id)
    variants = ProductVariant.objects.filter(product=product)

    with open(f"{product.name}_variants.csv", "w", newline="") as csvfile:
        fieldnames = ["Color", "Size", "Price", "Stock", "Warehouse"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for variant in variants:
            writer.writerow(
                {
                    "Color": variant.color,
                    "Size": variant.size,
                    "Price": variant.price,
                    "Stock": variant.stock,
                    "Warehouse": variant.warehouse.name,
                }
            )


def import_product_variants_from_csv(product_id, csv_file):
    """
    Import product variants from CSV for a specific product.
    """
    product = Product.objects.get(id=product_id)
    reader = csv.DictReader(csv_file)
    for row in reader:
        warehouse = Warehouse.objects.get(name=row["Warehouse"])
        ProductVariant.objects.create(
            product=product,
            color=row["Color"],
            size=row["Size"],
            price=row["Price"],
            stock=row["Stock"],
            warehouse=warehouse,
        )


def search_variants_by_attributes(product, color=None, size=None, price_range=None):
    """
    Search product variants by color, size, and price range.
    """
    variants = ProductVariant.objects.filter(product=product)

    if color:
        variants = variants.filter(color=color)

    if size:
        variants = variants.filter(size=size)

    if price_range:
        min_price, max_price = price_range
        variants = variants.filter(price__gte=min_price, price__lte=max_price)

    return variants
