from .models import Product, ProductVariant
from .utils import BaseSKUGenerator, ProductValidation, VariantSKUGenerator


class ProductService:
    """
    Service layer that interacts with SKU generators and ProductValidation to handle business logic.
    Adheres to OCP by allowing extension of SKU generation without modification.
    """

    def __init__(
        self,
        base_sku_generator: BaseSKUGenerator,
        variant_sku_generator: VariantSKUGenerator,
        validation: ProductValidation,
    ):
        """
        Use Dependency Injection to decouple services from concrete implementations.
        """
        self.base_sku_generator = base_sku_generator
        self.variant_sku_generator = variant_sku_generator
        self.validation = validation

    def create_product(self, product_data, variant_data_list):
        """
        Create a product with associated variants.
        :param product_data: Dictionary containing product fields.
        :param variant_data_list: List of dictionaries containing variant fields.
        :return: Product instance with its variants created.
        """
        # Create product
        product = Product.objects.create(**product_data)

        if variant_data_list:
            # Create variants and assign SKU for each variant
            for variant_data in variant_data_list:
                self.validation.validate_variant_uniqueness(product, variant_data)
                variant = ProductVariant(product=product, **variant_data)
                variant_sku = self.variant_sku_generator.generate_sku(
                    product, variant_data
                )
                product.sku = variant_sku  # SKU for product will depend on variant
                variant.save()
        else:
            # Generate SKU for base product without variants
            base_sku = self.base_sku_generator.generate_sku(product)
            product.sku = base_sku

        product.save()
        return product

    def update_variant_sku(self, variant: ProductVariant) -> str:
        """
        Update the SKU of a product variant when its attributes are changed.
        :param variant: The product variant.
        :return: Updated SKU.
        """
        updated_sku = self.variant_sku_generator.generate_sku(variant.product, variant)

        # Ensure uniqueness of the new SKU
        while not self.variant_sku_generator.is_sku_unique(updated_sku):
            updated_sku = self.variant_sku_generator.generate_sku(
                variant.product, variant
            )

        variant.sku = updated_sku
        variant.save()
        return variant.sku


class StockService:
    """
    A specialized service to handle stock-related operations.
    Adheres to SRP and DIP by interacting only with high-level abstractions.
    """

    @staticmethod
    def is_variant_in_stock(variant: ProductVariant, requested_quantity: int) -> bool:
        """
        Check if the product variant has enough stock for the requested quantity.
        :param variant: The product variant.
        :param requested_quantity: The quantity requested.
        :return: True if stock is sufficient, False otherwise.
        """
        return variant.stock >= requested_quantity


class CSVExportService:
    """
    Handles exporting products to CSV. Adheres to SRP by focusing on exporting logic.
    """

    @staticmethod
    def export_products_to_csv(queryset):
        import csv

        from django.http import HttpResponse

        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="products.csv"'

        writer = csv.writer(response)
        writer.writerow(["Name", "SKU", "Category", "Price"])

        for product in queryset:
            writer.writerow(
                [product.name, product.sku, product.category.name, product.price]
            )

        return response


def create_product_with_variants(data):
    product = Product.objects.create(
        name=data["name"],
        brand=data["brand"],
        category=data["category"],
        base_price=data["base_price"],
        description=data["description"],
    )

    # Generate the SKU for the product
    # TODO Create generate_product_sku function
    # product.sku = generate_product_sku(product)
    product.save()

    # Create variants for the product
    for variant_data in data["variants"]:
        variant = ProductVariant.objects.create(
            product=product,
            color=variant_data.get("color"),
            size=variant_data.get("size"),
            price=variant_data.get("price"),
            stock=variant_data.get("stock"),
        )
        # Generate SKU for variant
        # TODO Create generate_variant_sku function
        # variant.sku = generate_variant_sku(product.sku, variant)
        variant.save()
