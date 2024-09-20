from django.contrib import admin
from django.contrib import admin
from .models import Order, OrderItem, Payment

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['total_price']
    fields = ['product', 'quantity', 'price_per_item', 'total_price']

class PaymentInline(admin.StackedInline):
    model = Payment
    extra = 0
    readonly_fields = ['payment_date']

class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer', 'order_date', 'status', 'total_amount', 'payment_status', 'shipping_address', 'number_of_items']
    list_filter = ['status', 'order_date', 'payment_status']
    search_fields = ['customer__name', 'id', 'shipping_address']
    inlines = [OrderItemInline, PaymentInline]
    readonly_fields = ['total_amount']
    ordering = ['-order_date']
    
    actions = ['mark_as_processed', 'mark_as_shipped', 'cancel_orders']

    def mark_as_processed(self, request, queryset):
        updated = queryset.update(status='processed')
        self.message_user(request, f'{updated} orders marked as Processed.')
    mark_as_processed.short_description = 'Mark selected orders as Processed'

    def mark_as_shipped(self, request, queryset):
        updated = queryset.update(status='shipped')
        self.message_user(request, f'{updated} orders marked as Shipped.')
    mark_as_shipped.short_description = 'Mark selected orders as Shipped'

    def cancel_orders(self, request, queryset):
        updated = queryset.update(status='canceled')
        self.message_user(request, f'{updated} orders canceled.')
    cancel_orders.short_description = 'Cancel selected orders'

    def number_of_items(self, obj):
        return obj.items.count()
    number_of_items.short_description = 'Number of Items'

class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product', 'quantity', 'price_per_item', 'total_price']
    search_fields = ['order__id', 'product__name']
    list_filter = ['product__name', 'order__status']

class PaymentAdmin(admin.ModelAdmin):
    list_display = ['order', 'payment_method', 'payment_status', 'payment_date']
    list_filter = ['payment_status', 'payment_method']
    search_fields = ['order__id', 'payment_status']

    actions = ['mark_as_paid', 'mark_as_pending']

    def mark_as_paid(self, request, queryset):
        updated = queryset.update(payment_status='paid')
        self.message_user(request, f'{updated} payments marked as Paid.')
    mark_as_paid.short_description = 'Mark selected payments as Paid'

    def mark_as_pending(self, request, queryset):
        updated = queryset.update(payment_status='pending')
        self.message_user(request, f'{updated} payments marked as Pending.')
    mark_as_pending.short_description = 'Mark selected payments as Pending'

admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem, OrderItemAdmin)
admin.site.register(Payment, PaymentAdmin)
