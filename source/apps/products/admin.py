from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from .models import Brand, Category, Product, ProductImages, ProductVariant


class BrandAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "image_tag", "description")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ("image_tag",)

    def image_tag(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width: 50px; height: 50px;" />', obj.image.url
            )
        return "-"

    image_tag.short_description = "Image"


admin.site.register(Brand, BrandAdmin)


class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "parent", "image_tag", "description")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}
    list_filter = ("parent",)
    readonly_fields = ("image_tag",)

    def image_tag(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width: 50px; height: 50px;" />', obj.image.url
            )
        return "-"

    image_tag.short_description = "Image"

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related("parent")


admin.site.register(Category, CategoryAdmin)


class ProductImagesInline(admin.TabularInline):
    model = ProductImages
    extra = 1


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1
    fields = (
        "color",
        "size",
        "price",
        "sku",
        "weight",
        "dimensions",
        "stock",
        "variant_group",
        "is_active",
    )
    readonly_fields = ("stock",)


class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "brand",
        "category",
        "base_price",
        "image_tag",
        "flag",
        "slug",
        "sku",
        "is_active",
        "created_at",
    )
    list_filter = ("brand", "category", "flag", "is_active", "created_at")
    search_fields = ("name", "sku", "description")
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = (
        "total_stock",
        "image_tag",
    )
    inlines = [ProductImagesInline, ProductVariantInline]
    # filter_horizontal = ('tags',)

    def image_tag(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width: 50px; height: 50px;" />', obj.image.url
            )
        return "-"

    image_tag.short_description = "Image"

    def total_stock(self, obj):
        return obj.total_stock()

    total_stock.short_description = _("Total Stock")

    # def save_model(self, request, obj, form, change):
    #     # Ensure unique SKU logic here if needed
    #     super().save_model(request, obj, form, change)


admin.site.register(Product, ProductAdmin)


class ProductVariantAdmin(admin.ModelAdmin):
    list_display = (
        "product",
        "color",
        "size",
        "price",
        "stock",
        "sku",
        "variant_group",
        "is_active",
    )
    list_filter = ("color", "size", "variant_group", "is_active")
    search_fields = ("product__name", "sku", "color", "size")
    readonly_fields = ("stock",)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("product")


admin.site.register(ProductVariant, ProductVariantAdmin)


class ProductImagesAdmin(admin.ModelAdmin):
    list_display = ("product", "image_tag")
    readonly_fields = ("image_tag",)

    def image_tag(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width: 50px; height: 50px;" />', obj.image.url
            )
        return "-"

    image_tag.short_description = "Image"


admin.site.register(ProductImages, ProductImagesAdmin)
