from django.contrib import admin
from products.models import Product, Category

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent')
    search_fields = ('name',)
    list_filter = ('parent',)

class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'sku', 'category', 'price', 'created_at', 'updated_at')
    search_fields = ('name', 'sku')
    list_filter = ('category',)
    ordering = ('-created_at',)
    prepopulated_fields = {"sku": ("name",)}


admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)