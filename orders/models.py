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

class Cart(models.Model):
    customer = models.ForeignKey(
        Customer, on_delete=models.CASCADE, related_name='carts', null=True, blank=True
    )
    session_key = models.CharField(max_length=40, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_quantity = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = 'Cart'
        verbose_name_plural = 'Carts'
        ordering = ['-created_at']
        
    def clear(self):
        """Clears all items from the cart."""
        self.items.all().delete()
        self.calculate_totals()

    def calculate_totals(self):
        """Calculates and updates the cart's total price and quantity."""
        total = Decimal('0.00')
        quantity = 0
        for item in self.items.all():
            total += item.total_price
            quantity += item.quantity
        self.total_price = total
        self.total_quantity = quantity
        self.save(update_fields=['total_price', 'total_quantity'])

    def add_item(self, product, quantity=1):
        """Adds an item to the cart or updates its quantity."""
        cart_item, created = self.items.get_or_create(product=product)
        if not created:
            cart_item.quantity += quantity
        else:
            cart_item.quantity = quantity
            cart_item.price_per_item = product.price
        cart_item.save()
        self.calculate_totals()

    def remove_item(self, product):
        """Removes an item from the cart."""
        try:
            cart_item = self.items.get(product=product)
            cart_item.delete()
            self.calculate_totals()
        except CartItem.DoesNotExist:
            pass

    def get_absolute_url(self):
        return reverse('cart_detail', args=[str(self.id)])

        
    def total_quantity(self):
        return sum(item.quantity for item in self.items.all())

    def __str__(self):
        if self.customer:
            return f'Cart {self.id} - {self.customer.get_full_name()}'
        else:
            return f'Cart {self.id} - Session {self.session_key}'



class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='cart_items')
    quantity = models.PositiveIntegerField(default=1)
    price_per_item = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    added_at = models.DateTimeField(auto_now_add=True, null=True)

    def save(self, *args, **kwargs):
        self.total_price = self.quantity * self.price_per_item
        super().save(*args, **kwargs)
        self.cart.calculate_total()

    def __str__(self):
        return f'{self.quantity} x {self.product.name} in Cart {self.cart.id}'


    class Meta:
        verbose_name = 'Cart Item'
        verbose_name_plural = 'Cart Items'
        unique_together = ('cart', 'product')

    def save(self, *args, **kwargs):
        self.price_per_item = self.product.price
        self.total_price = self.quantity * self.price_per_item
        super().save(*args, **kwargs)
        self.cart.calculate_totals()

    def get_absolute_url(self):
        return reverse('cart_item_detail', args=[str(self.id)])


class CartCoupon(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='coupons')
    code = models.CharField(max_length=50)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2)
    applied_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Coupon {self.code} applied to Cart {self.cart.id}'

    class Meta:
        verbose_name = 'Cart Coupon'
        verbose_name_plural = 'Cart Coupons'
        unique_together = ('cart', 'code')


class CartHistory(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='history')
    status = models.CharField(max_length=50, choices=[
        ('created', 'Created'),
        ('updated', 'Updated'),
        ('checked_out', 'Checked Out'),
        ('abandoned', 'Abandoned'),
    ], default='created')
    timestamp = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f'Cart {self.cart.id} - {self.status} at {self.timestamp}'

    class Meta:
        verbose_name = 'Cart History'
        verbose_name_plural = 'Cart Histories'
        ordering = ['-timestamp']
