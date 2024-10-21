from django.db import models
from source.apps.products.models import Product
from source.apps.customers.models import Customer
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from django.core.validators import MinValueValidator
from django.urls import reverse
from .managers import CartManager
import uuid


class Cart(models.Model):
    customer = models.ForeignKey(
        Customer, on_delete=models.CASCADE, related_name="carts", null=True, blank=True
    )
    session_key = models.CharField(max_length=40, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_quantity = models.PositiveIntegerField(default=0)
    objects = CartManager()

    class Meta:
        verbose_name = "Cart"
        verbose_name_plural = "Carts"
        ordering = ["-created_at"]
        constraints = [
            models.CheckConstraint(
                check=models.Q(total_quantity__gte=0), name="cart_quantity_non_negative"
            )
        ]

    def clean(self):
        # Ensure either session_key or customer is present, but not both
        if not self.customer and not self.session_key:
            self.session_key = str(uuid.uuid4())
        if not self.customer and not self.session_key:
            raise ValueError("Either customer or session_key must be set for a cart.")
        if self.customer and self.session_key:
            raise ValueError("Cart cannot have both customer and session_key.")

    def is_guest_cart(self):
        return self.customer is None

    def checkout(self, shipping_address, payment_method=None):
        from source.apps.orders.models import Order, OrderItem

        if not self.items.exists():
            raise ValueError("Cannot checkout an empty cart")

        # Create the order
        order = Order.objects.create(
            customer=self.customer,
            total_amount=self.total_price,
            shipping_address=shipping_address,
            payment_method=payment_method,
            status="pending",
            payment_status="unpaid",
        )

        # Move cart items to order items
        for item in self.items.all():
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price_per_item=item.price_per_item,
                total_price=item.total_price,
            )

        # Update inventory, handle fulfillment, etc.
        self.clear_cart()
        CartHistory.objects.create(cart=self, status="checked_out")

    def clear_cart(self):
        """Clear the cart items after checkout."""
        self.items.all().delete()
        self.total_price = 0
        self.total_quantity = 0
        self.is_active = False
        self.save(update_fields=["total_price", "total_quantity", "is_active"])

    @staticmethod
    def clear_expired_carts():
        expiration_date = timezone.now() - timedelta(days=30)
        expired_carts = Cart.objects.filter(
            updated_at__lt=expiration_date, is_active=True
        )
        for cart in expired_carts:
            cart.clear_cart()
            CartHistory.objects.create(cart=cart, status="abandoned")

    def calculate_totals(self):
        """Calculates and updates the cart's total price and quantity."""
        total = Decimal("0.00")
        quantity = 0
        for item in self.items.all():
            total += item.total_price
            quantity += item.quantity
        self.total_price = total
        self.total_quantity = quantity
        self.save(update_fields=["total_price", "total_quantity"])

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

    def apply_coupon(self, coupon):
        """Apply a valid coupon to the cart."""
        if not isinstance(coupon, CartCoupon):
            raise ValueError("Invalid coupon type")
        if self.coupons.filter(code=coupon.code).exists():
            raise ValueError("Coupon already applied")
        self.coupons.add(coupon)
        self.calculate_totals()

    def get_absolute_url(self):
        return reverse("cart_detail", args=[str(self.id)])

    def __str__(self):
        if self.customer:
            return f"Cart {self.id} - {self.customer.get_full_name()}"
        else:
            return f"Cart {self.id} - Session {self.session_key}"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="cart_items"
    )
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    price_per_item = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    added_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        verbose_name = "Cart Item"
        verbose_name_plural = "Cart Items"
        constraints = [
            models.UniqueConstraint(
                fields=["cart", "product"], name="unique_cart_product"
            )
        ]

    def save(self, *args, **kwargs):
        self.price_per_item = self.product.price
        self.total_price = self.quantity * self.price_per_item
        super().save(*args, **kwargs)
        self.cart.calculate_totals()

    def __str__(self):
        return f"{self.quantity} x {self.product.name} in Cart {self.cart.id}"

    def get_absolute_url(self):
        return reverse("cart_item_detail", args=[str(self.id)])


class CartCoupon(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="coupons")
    code = models.CharField(max_length=50)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2)
    applied_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Cart Coupon"
        verbose_name_plural = "Cart Coupons"
        constraints = [
            models.UniqueConstraint(fields=["cart", "code"], name="unique_cart_coupon")
        ]

    def __str__(self):
        return f"Coupon {self.code} applied to Cart {self.cart.id}"


class CartHistory(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="history")
    status = models.CharField(
        max_length=50,
        choices=[
            ("created", "Created"),
            ("updated", "Updated"),
            ("checked_out", "Checked Out"),
            ("abandoned", "Abandoned"),
        ],
        default="created",
    )
    timestamp = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Cart History"
        verbose_name_plural = "Cart Histories"
        ordering = ["-timestamp"]

    def __str__(self):
        return f"Cart {self.cart.id} - {self.status} at {self.timestamp}"
