from django.contrib import admin
from django.urls import path, reverse
from django.template.response import TemplateResponse
from .models import Order, OrderItem, Payment, RepairOrder
from .services import RepairCalculationService
from django.utils.html import format_html
from .filters import UnpaidFilter, CompletedFilter, SentToOtherShopFilter


@admin.register(RepairOrder)
class RepairOrderAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "code",
        "customer_name",
        "device_name",
        "status",
        "total_price",
        "expenses",
        "profit",
        "created_at",
        "completion_time",
    ]
    list_filter = [
        UnpaidFilter,
        CompletedFilter,
        SentToOtherShopFilter,
        "status",
        "created_at",
        "shop",
        "device_type",
    ]
    search_fields = ["customer_name", "device_name", "id", "customer_contact"]
    readonly_fields = ["profit", "created_at"]
    actions = [
        "mark_as_completed",
        "mark_as_awaiting_pickup",
        "mark_as_paid",
        "print_receipt",
    ]
    ordering = ["-created_at"]

    def print_receipt(self, request, queryset):
        for order in queryset:
            url = reverse("repair_receipt", args=[order.pk])
            return format_html('<a class="button" href="{}">Print Receipt</a>', url)

    print_receipt.short_description = "Print Repair Receipt"

    # Custom daily report view included in changelist view
    def changelist_view(self, request, extra_context=None):
        # Add a button to link to the daily report
        extra_context = extra_context or {}
        extra_context["daily_report_button"] = format_html(
            '<a class="button" href="{}">Go to Daily Report</a>',
            "/admin/orders/repairorder/daily-report/",
        )

        # Fetch the daily totals from the service (optional)
        daily_totals = RepairCalculationService.calculate_daily_totals()
        extra_context.update(
            {
                "daily_totals": daily_totals,
                "total_orders": daily_totals["total_orders"],
                "total_price": daily_totals["total_price"],
                "total_expenses": daily_totals["total_expenses"],
                "total_profit": daily_totals["total_profit"],
                "profit_owner": daily_totals["profit_owner"],
                "profit_worker": daily_totals["profit_worker"],
                "unpaid_orders_count": daily_totals["unpaid_orders_count"],
                "unpaid_total": daily_totals["unpaid_total"],
            }
        )

        return super().changelist_view(request, extra_context=extra_context)

    # Add the custom URL for the daily report page (if needed)
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "daily-report/",
                self.admin_site.admin_view(self.daily_report_view),
                name="daily-report",
            ),
        ]
        return custom_urls + urls

    def daily_report_view(self, request):
        daily_totals = RepairCalculationService.calculate_daily_totals()

        context = dict(
            self.admin_site.each_context(request),
            daily_totals=daily_totals,
            total_orders=daily_totals["total_orders"],
            total_price=daily_totals["total_price"],
            total_expenses=daily_totals["total_expenses"],
            total_profit=daily_totals["total_profit"],
            profit_owner=daily_totals["profit_owner"],
            profit_worker=daily_totals["profit_worker"],
            unpaid_orders_count=daily_totals["unpaid_orders_count"],
            unpaid_total=daily_totals["unpaid_total"],
        )

        return TemplateResponse(request, "admin/daily_report.html", context)

    def mark_as_completed(self, request, queryset):
        updated = queryset.update(status="completed")
        self.message_user(request, f"{updated} orders marked as Completed.")

    mark_as_completed.short_description = "Mark selected orders as Completed"

    def mark_as_awaiting_pickup(self, request, queryset):
        updated = queryset.update(status="customer_pickup")
        self.message_user(request, f"{updated} orders marked as Awaiting Pickup.")

    mark_as_awaiting_pickup.short_description = (
        "Mark selected orders as Awaiting Pickup"
    )

    def mark_as_paid(self, request, queryset):
        updated = queryset.update(status="paid", payment_received=True)
        self.message_user(request, f"{updated} orders marked as Paid.")

    mark_as_paid.short_description = "Mark selected orders as Paid"


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ["total_price"]
    fields = ["product", "quantity", "price_per_item", "total_price"]


class PaymentInline(admin.StackedInline):
    model = Payment
    extra = 0
    readonly_fields = ["payment_date"]


class OrderAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "customer",
        "order_date",
        "status",
        "total_amount",
        "payment_status",
        "shipping_address",
        "number_of_items",
    ]
    list_filter = ["status", "order_date", "payment_status"]
    search_fields = ["customer__name", "id", "shipping_address"]
    inlines = [OrderItemInline, PaymentInline]
    readonly_fields = ["total_amount"]
    ordering = ["-order_date"]

    actions = ["mark_as_processed", "mark_as_shipped", "cancel_orders"]

    def mark_as_processed(self, request, queryset):
        updated = queryset.update(status="processed")
        self.message_user(request, f"{updated} orders marked as Processed.")

    mark_as_processed.short_description = "Mark selected orders as Processed"

    def mark_as_shipped(self, request, queryset):
        updated = queryset.update(status="shipped")
        self.message_user(request, f"{updated} orders marked as Shipped.")

    mark_as_shipped.short_description = "Mark selected orders as Shipped"

    def cancel_orders(self, request, queryset):
        updated = queryset.update(status="canceled")
        self.message_user(request, f"{updated} orders canceled.")

    cancel_orders.short_description = "Cancel selected orders"

    def number_of_items(self, obj):
        return obj.items.count()

    number_of_items.short_description = "Number of Items"


class OrderItemAdmin(admin.ModelAdmin):
    list_display = ["order", "product", "quantity", "price_per_item", "total_price"]
    search_fields = ["order__id", "product__name"]
    list_filter = ["product__name", "order__status"]


class PaymentAdmin(admin.ModelAdmin):
    list_display = ["order", "payment_method", "payment_status", "payment_date"]
    list_filter = ["payment_status", "payment_method"]
    search_fields = ["order__id", "payment_status"]

    actions = ["mark_as_paid", "mark_as_pending"]

    def mark_as_paid(self, request, queryset):
        updated = queryset.update(payment_status="paid")
        self.message_user(request, f"{updated} payments marked as Paid.")

    mark_as_paid.short_description = "Mark selected payments as Paid"

    def mark_as_pending(self, request, queryset):
        updated = queryset.update(payment_status="pending")
        self.message_user(request, f"{updated} payments marked as Pending.")

    mark_as_pending.short_description = "Mark selected payments as Pending"


admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem, OrderItemAdmin)
admin.site.register(Payment, PaymentAdmin)
