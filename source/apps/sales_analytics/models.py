from django.db import models
from source.apps.products.models import Product


class SalesReport(models.Model):
    report_date = models.DateField(auto_now_add=True)
    total_sales = models.DecimalField(max_digits=10, decimal_places=2)
    total_orders = models.PositiveIntegerField()
    total_customers = models.PositiveIntegerField()
    average_order_value = models.DecimalField(max_digits=10, decimal_places=2)
    highest_selling_product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        null=True,
        related_name="highest_selling_product",
    )

    class Meta:
        verbose_name = "Sales Report"
        verbose_name_plural = "Sales Reports"
        ordering = ["-report_date"]
        indexes = [
            models.Index(fields=["report_date"]),
        ]

    def calculate_average_order_value(self):
        if self.total_orders > 0:
            self.average_order_value = self.total_sales / self.total_orders
        else:
            self.average_order_value = 0
        self.save()

    def __str__(self):
        return f"Sales Report - {self.report_date}"


class SalesByProduct(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="sales_data"
    )
    total_units_sold = models.PositiveIntegerField()
    total_revenue = models.DecimalField(max_digits=10, decimal_places=2)
    report = models.ForeignKey(
        SalesReport, on_delete=models.CASCADE, related_name="sales_by_product"
    )

    class Meta:
        verbose_name = "Sales by Product"
        verbose_name_plural = "Sales by Product"
        ordering = ["-total_units_sold"]
        constraints = [
            models.CheckConstraint(
                check=models.Q(total_units_sold__gte=0), name="total_units_non_negative"
            ),
            models.CheckConstraint(
                check=models.Q(total_revenue__gte=0), name="total_revenue_non_negative"
            ),
        ]

    def calculate_total_revenue(self):
        self.total_revenue = self.total_units_sold * self.product.price
        self.save()

    def __str__(self):
        return f"{self.product.name} - {self.total_units_sold} units"


class SalesByCustomerSegment(models.Model):
    segment = models.CharField(max_length=100)
    total_sales = models.DecimalField(max_digits=10, decimal_places=2)
    total_orders = models.PositiveIntegerField()
    report = models.ForeignKey(
        SalesReport, on_delete=models.CASCADE, related_name="sales_by_segment"
    )

    class Meta:
        verbose_name = "Sales by Customer Segment"
        verbose_name_plural = "Sales by Customer Segments"
        ordering = ["segment"]
        constraints = [
            models.CheckConstraint(
                check=models.Q(total_sales__gte=0), name="total_sales_non_negative"
            ),
            models.CheckConstraint(
                check=models.Q(total_orders__gte=0), name="total_orders_non_negative"
            ),
        ]

    def calculate_average_sales_per_order(self):
        if self.total_orders > 0:
            return self.total_sales / self.total_orders
        return 0

    def __str__(self):
        return f"{self.segment} Segment Sales"
