from django.db import models
from inventory.models import Product
from customers.models import Customer
from django.utils import timezone

class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='orders')
    order_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, choices=[
        ('pending', 'Pending'),
        ('processed', 'Processed'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('canceled', 'Canceled'),
    ], default='pending')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_address = models.CharField(max_length=255)
    payment_status = models.CharField(max_length=50, choices=[
        ('paid', 'Paid'),
        ('unpaid', 'Unpaid'),
        ('refunded', 'Refunded'),
    ], default='unpaid')

    class Meta:
        constraints = [
            models.CheckConstraint(check=models.Q(total_amount__gte=0), name='total_amount_non_negative')
        ]

    def update_status(self, new_status):
        self.status = new_status
        self.save()

    def cancel_order(self):
        if self.status in ['shipped', 'delivered']:
            raise ValueError("Cannot cancel order after it has been shipped or delivered")
        self.status = 'canceled'
        self.save()

    def calculate_total(self):
        self.total_amount = sum(item.total_price for item in self.items.all())
        self.save()

    def __str__(self):
        return f'Order {self.id} - {self.customer.name}'
    
class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='order_items')
    quantity = models.IntegerField()
    price_per_item = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    def calculate_total_price(self):
        self.total_price = self.quantity * self.price_per_item
        self.save()

    def __str__(self):
        return f'{self.quantity} of {self.product.name} for Order {self.order.id}'
    
class Payment(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='payment')
    payment_method = models.CharField(max_length=50, choices=[
        ('credit_card', 'Credit Card'),
        ('paypal', 'PayPal'),
        ('cash_on_delivery', 'Cash on Delivery'),
    ])
    payment_date = models.DateTimeField(null=True, blank=True)
    payment_status = models.CharField(max_length=50, choices=[
        ('paid', 'Paid'),
        ('pending', 'Pending'),
        ('failed', 'Failed'),
    ], default='pending')
    
    def process_payment(self, method):
        # Add actual payment processing logic (e.g., integration with PayPal API)
        self.payment_method = method
        self.payment_status = 'paid'
        self.payment_date = timezone.now()
        self.save()


    def __str__(self):
        return f'Payment for Order {self.order.id} - {self.payment_status}'
