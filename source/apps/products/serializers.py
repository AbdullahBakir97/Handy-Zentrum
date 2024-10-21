from rest_framework import serializers
from .models import Brand, Category, Product, ProductImages, ProductVariant
from django.utils.text import slugify


# Brand Serializer
class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ["id", "name", "description", "slug", "image"]

    def validate_slug(self, value):
        if not value:
            value = slugify(self.initial_data.get("name"))
        return value


# Category Serializer
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "description", "slug", "parent", "image"]

    def validate(self, data):
        if data.get("parent") == self.instance:
            raise serializers.ValidationError("A category cannot be its own parent.")
        return data

    def validate_slug(self, value):
        if not value:
            value = slugify(self.initial_data.get("name"))
        return value


# Product Serializer
class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    brand = BrandSerializer(read_only=True)
    tags = serializers.StringRelatedField(many=True)

    class Meta:
        model = Product
        fields = [
            "id",
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
            "is_active",
            "created_at",
            "updated_at",
        ]

    def validate_slug(self, value):
        if not value:
            value = slugify(self.initial_data.get("name"))
        return value

    def validate_sku(self, value):
        if not value:
            from .utils import BaseSKUGenerator

            sku_generator = BaseSKUGenerator()
            value = sku_generator.generate_sku(self.instance)
        return value


# Product Images Serializer
class ProductImagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImages
        fields = ["id", "product", "image"]


# Product Variant Serializer
class ProductVariantSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model = ProductVariant
        fields = [
            "id",
            "product",
            "color",
            "size",
            "sku",
            "price",
            "weight",
            "dimensions",
            "stock",
            "variant_group",
            "is_active",
        ]

    def validate(self, data):
        # Ensure the uniqueness of the color and size combination per product
        if ProductVariant.objects.filter(
            product=data.get("product"), color=data.get("color"), size=data.get("size")
        ).exists():
            raise serializers.ValidationError(
                "This combination of color and size already exists for the selected product."
            )
        return data

    def validate_sku(self, value):
        if not value:
            product = self.initial_data.get("product")
            color = self.initial_data.get("color")
            size = self.initial_data.get("size")
            value = f"{product.sku}-{color[:1].upper()}-{size[:1].upper()}"
        return value
