from django.contrib import admin

from .models import Cart, CartItem, CartCoupon, CartHistory


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ('price_per_item', 'total_price')

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'customer', 'session_key', 'total_quantity', 'total_price', 'is_active', 'created_at', 'updated_at'
    )
    list_filter = ('is_active', 'created_at', 'updated_at')
    search_fields = ('customer__first_name', 'customer__last_name', 'session_key')
    inlines = [CartItemInline]
    readonly_fields = ('total_price', 'total_quantity', 'created_at', 'updated_at')

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'cart', 'product', 'quantity', 'price_per_item', 'total_price', 'added_at')
    list_filter = ('added_at',)
    search_fields = ('product__name', 'cart__id')

@admin.register(CartCoupon)
class CartCouponAdmin(admin.ModelAdmin):
    list_display = ('id', 'cart', 'code', 'discount_amount', 'applied_at')
    list_filter = ('applied_at',)
    search_fields = ('code', 'cart__id')

@admin.register(CartHistory)
class CartHistoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'cart', 'status', 'timestamp')
    list_filter = ('status', 'timestamp')
    search_fields = ('cart__id',)
