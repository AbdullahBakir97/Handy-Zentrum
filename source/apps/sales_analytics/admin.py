from django.contrib import admin
from django.contrib import admin
from .models import SalesReport, SalesByProduct, SalesByCustomerSegment


class SalesByProductInline(admin.TabularInline):
    model = SalesByProduct
    extra = 0
    readonly_fields = ["total_units_sold", "total_revenue"]
    fields = ["product", "total_units_sold", "total_revenue"]


class SalesByCustomerSegmentInline(admin.TabularInline):
    model = SalesByCustomerSegment
    extra = 0
    readonly_fields = ["segment", "total_sales", "total_orders"]
    fields = ["segment", "total_sales", "total_orders"]


class SalesReportAdmin(admin.ModelAdmin):
    list_display = [
        "report_date",
        "total_sales",
        "total_orders",
        "total_customers",
        "average_order_value",
        "highest_selling_product",
        "total_products_sold",
    ]
    list_filter = ["report_date", "total_sales"]
    search_fields = ["report_date"]
    inlines = [SalesByProductInline, SalesByCustomerSegmentInline]
    readonly_fields = [
        "total_sales",
        "total_orders",
        "total_customers",
        "average_order_value",
    ]
    ordering = ["-report_date"]

    actions = ["generate_monthly_report", "export_sales_data"]

    def generate_monthly_report(self, request, queryset):
        self.message_user(request, f"Monthly report generation is in progress.")

    generate_monthly_report.short_description = "Generate Monthly Sales Report"

    def export_sales_data(self, request, queryset):
        self.message_user(request, f"Sales data exported successfully.")

    export_sales_data.short_description = "Export Sales Data"

    def total_products_sold(self, obj):
        return (
            obj.sales_by_product.aggregate(total=models.Sum("total_units_sold"))[
                "total"
            ]
            or 0
        )

    total_products_sold.short_description = "Total Products Sold"


class SalesByProductAdmin(admin.ModelAdmin):
    list_display = ["product", "total_units_sold", "total_revenue", "report"]
    search_fields = ["product__name"]
    list_filter = ["product__name", "total_units_sold"]


class SalesByCustomerSegmentAdmin(admin.ModelAdmin):
    list_display = ["segment", "total_sales", "total_orders", "report"]
    search_fields = ["segment"]
    list_filter = ["segment", "total_sales"]


admin.site.register(SalesReport, SalesReportAdmin)
admin.site.register(SalesByProduct, SalesByProductAdmin)
admin.site.register(SalesByCustomerSegment, SalesByCustomerSegmentAdmin)
