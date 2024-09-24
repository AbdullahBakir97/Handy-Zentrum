from django.db import models
from inventory.models import Product
from customers.models import Customer
from django.utils import timezone
from decimal import Decimal
from django.core.validators import MinValueValidator
from django.urls import reverse

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
        ordering = ['-order_date']
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'
        constraints = [
            models.CheckConstraint(check=models.Q(total_amount__gte=0), name='total_amount_non_negative')
        ]

    def __str__(self):
        return f'Order {self.id} - {self.customer.name}'

    def update_status(self, new_status):
        """Update the order status."""
        if new_status not in ['pending', 'processed', 'shipped', 'delivered', 'canceled']:
            raise ValueError(f"Invalid status: {new_status}")
        self.status = new_status
        self.save()

    def cancel_order(self):
        """Cancel the order if it has not been shipped or delivered."""
        if self.status in ['shipped', 'delivered']:
            raise ValueError("Cannot cancel an order after it has been shipped or delivered.")
        self.status = 'canceled'
        self.save()

    def calculate_total(self):
        """Calculate and update the total amount of the order based on its items."""
        self.total_amount = sum(item.total_price for item in self.items.all())
        self.save()

    def refund(self):
        """Mark the order as refunded if it's paid."""
        if self.payment_status == 'paid':
            self.payment_status = 'refunded'
            self.status = 'canceled'
            self.save()
        else:
            raise ValueError("Only paid orders can be refunded.")

    
class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='order_items')
    quantity = models.IntegerField()
    price_per_item = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        ordering = ['order']
        verbose_name = 'Order Item'
        verbose_name_plural = 'Order Items'
        constraints = [
            models.CheckConstraint(check=models.Q(quantity__gte=1), name='quantity_non_negative')
        ]

    def __str__(self):
        return f'{self.quantity} of {self.product.name} for Order {self.order.id}'

    def calculate_total_price(self):
        """Calculate the total price for this item."""
        self.total_price = self.quantity * self.price_per_item
        self.save()

    
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
    
    class Meta:
        ordering = ['-payment_date']
        verbose_name = 'Payment'
        verbose_name_plural = 'Payments'

    def __str__(self):
        return f'Payment for Order {self.order.id} - {self.payment_status}'

    def process_payment(self, method):
        """Process the payment and mark it as 'paid'."""
        if self.order.status == 'canceled':
            raise ValueError("Cannot process payment for a canceled order.")
        self.payment_method = method
        self.payment_status = 'paid'
        self.payment_date = timezone.now()
        self.save()

    def refund_payment(self):
        """Refund the payment if it's already marked as paid."""
        if self.payment_status != 'paid':
            raise ValueError("Only paid payments can be refunded.")
        self.payment_status = 'refunded'
        self.payment_date = timezone.now()
        self.save()


