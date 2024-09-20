from django.contrib import admin
from .models import Category, Product, Warehouse, InventoryItem, StockAdjustment, InventoryTransfer

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

class InventoryItemInline(admin.TabularInline):
    model = InventoryItem
    extra = 1

class WarehouseAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'manager')
    search_fields = ('name', 'location', 'manager__username')
    inlines = [InventoryItemInline]

class InventoryItemAdmin(admin.ModelAdmin):
    list_display = ('product', 'location', 'quantity', 'status', 'last_updated')
    search_fields = ('product__name', 'location__name')
    list_filter = ('status', 'location')

class StockAdjustmentAdmin(admin.ModelAdmin):
    list_display = ('inventory_item', 'adjustment_type', 'quantity', 'performed_by', 'created_at')
    search_fields = ('inventory_item__product__name', 'performed_by__username')
    list_filter = ('adjustment_type', 'created_at')

class InventoryTransferAdmin(admin.ModelAdmin):
    list_display = ('product', 'from_location', 'to_location', 'quantity', 'status', 'created_at')
    search_fields = ('product__name', 'from_location__name', 'to_location__name', 'status')
    list_filter = ('status', 'created_at')

admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Warehouse, WarehouseAdmin)
admin.site.register(InventoryItem, InventoryItemAdmin)
admin.site.register(StockAdjustment, StockAdjustmentAdmin)
admin.site.register(InventoryTransfer, InventoryTransferAdmin)
