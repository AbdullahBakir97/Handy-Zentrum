from django.db import models
from inventory.models import Product

class SalesReport(models.Model):
    report_date = models.DateField(auto_now_add=True)
    total_sales = models.DecimalField(max_digits=10, decimal_places=2)
    total_orders = models.PositiveIntegerField()
    total_customers = models.PositiveIntegerField()
    average_order_value = models.DecimalField(max_digits=10, decimal_places=2)
    highest_selling_product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, related_name='highest_selling_product')

    def __str__(self):
        return f'Sales Report - {self.report_date}'

class SalesByProduct(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='sales_data')
    total_units_sold = models.PositiveIntegerField()
    total_revenue = models.DecimalField(max_digits=10, decimal_places=2)
    report = models.ForeignKey(SalesReport, on_delete=models.CASCADE, related_name='sales_by_product')

    def __str__(self):
        return f'{self.product.name} - {self.total_units_sold} units'
    
class SalesByCustomerSegment(models.Model):
    segment = models.CharField(max_length=100)
    total_sales = models.DecimalField(max_digits=10, decimal_places=2)
    total_orders = models.PositiveIntegerField()
    report = models.ForeignKey(SalesReport, on_delete=models.CASCADE, related_name='sales_by_segment')

    def __str__(self):
        return f'{self.segment} Segment Sales'