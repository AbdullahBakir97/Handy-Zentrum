from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone

from source.apps.customers.models import Customer
from source.apps.inventory.models import Warehouse
from source.apps.products.models import Product

from .managers import OrderManager, RepairOrderManager


class RepairOrder(models.Model):
    DEVICE_TYPES = [
        ("phone", "Phone"),
        ("tablet", "Tablet"),
        ("laptop", "Laptop"),
        ("other", "Other"),
    ]

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("in_progress", "In Progress"),
        ("completed", "Completed"),
        ("customer_pickup", "Awaiting Pickup"),
        ("paid", "Paid"),
        ("sent_to_other_shop", "Sent to Other Shop"),
    ]

    code = models.CharField(max_length=12, unique=True, blank=True, null=True)
    shop = models.ForeignKey(
        Warehouse, on_delete=models.CASCADE, related_name="repair_orders"
    )
    device_type = models.CharField(max_length=50, choices=DEVICE_TYPES)
    device_name = models.CharField(max_length=100)
    issue = models.TextField()
    total_price = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal("0.00"))]
    )
    expenses = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal("0.00"))]
    )
    profit = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, editable=False
    )
    created_at = models.DateTimeField(auto_now_add=True)
    completion_time = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default="pending")
    details = models.TextField(blank=True, null=True)
    customer_name = models.CharField(max_length=100, blank=True)
    customer_contact = models.CharField(max_length=50, blank=True)
    payment_received = models.BooleanField(default=False)
    payment_pending_reason = models.CharField(
        max_length=100, null=True, blank=True
    )  # e.g., "Awaiting Customer Pickup" or "Sent to Other Shop"
    objects = RepairOrderManager()

    class Meta:
        ordering = ["-created_at"]

    def calculate_profit(self):
        """Calculate profit as total price minus expenses."""
        if self.expenses is not None and self.total_price is not None:
            self.profit = self.total_price - self.expenses
        else:
            self.profit = 0

    def is_paid(self):
        """Check if the order is marked as paid."""
        return self.status == "paid"

    def is_sent_to_other_shop(self):
        """Check if the order is sent to another shop."""
        return self.status == "sent_to_other_shop"

    def is_completed(self):
        """Check if the repair is completed but not yet paid or picked up."""
        return self.status == "completed" or self.status == "customer_pickup"

    def mark_payment_pending(self, reason):
        """Mark this order as having pending payment."""
        self.payment_received = False
        self.payment_pending_reason = reason
        self.save()

    def mark_paid(self):
        """Mark the order as paid and payment received."""
        self.payment_received = True
        self.payment_pending_reason = None
        self.save()

    def save(self, *args, **kwargs):
        """Override the save method to ensure profit is calculated before saving."""
        self.calculate_profit()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.device_name} - {self.issue} ({self.status}) - {self.code}"


class Order(models.Model):
    customer = models.ForeignKey(
        Customer, on_delete=models.CASCADE, related_name="orders"
    )
    order_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=50,
        choices=[
            ("pending", "Pending"),
            ("processed", "Processed"),
            ("shipped", "Shipped"),
            ("delivered", "Delivered"),
            ("canceled", "Canceled"),
        ],
        default="pending",
    )
    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
        default=Decimal("0.00"),
    )
    shipping_address = models.CharField(max_length=255)
    payment_status = models.CharField(
        max_length=50,
        choices=[
            ("paid", "Paid"),
            ("unpaid", "Unpaid"),
            ("refunded", "Refunded"),
        ],
        default="unpaid",
    )
    objects = OrderManager

    class Meta:
        ordering = ["-order_date"]
        verbose_name = "Order"
        verbose_name_plural = "Orders"
        constraints = [
            models.CheckConstraint(
                check=models.Q(total_amount__gte=0), name="total_amount_non_negative"
            )
        ]

    def __str__(self):
        return f"Order {self.id} - {self.customer.user}"

    # def save(self, *args, **kwargs):
    #     # Ensure total_amount is calculated before saving if not already set
    #     if not self.pk and self.total_amount == Decimal('0.00'):
    #         self.total_amount = self.calculate_total()
    #     super().save(*args, **kwargs)

    def update_status(self, new_status):
        """Update the order status."""
        if new_status not in dict(self._meta.get_field("status").choices):
            raise ValueError(f"Invalid status: {new_status}")
        self.status = new_status
        self.save(update_fields=["status"])

    def cancel_order(self):
        """Cancel the order if it has not been shipped or delivered."""
        if self.status in ["shipped", "delivered"]:
            raise ValueError(
                "Cannot cancel an order after it has been shipped or delivered."
            )
        self.status = "canceled"
        self.save(update_fields=["status"])

    def calculate_total(self):
        """Calculate the total amount for the order based on its items."""
        total = sum(item.total_price for item in self.items.all())
        return total

    def refund(self):
        """Mark the order as refunded if it's paid."""
        if self.payment_status == "paid":
            self.payment_status = "refunded"
            self.status = "canceled"
            self.save(update_fields=["payment_status", "status"])
        else:
            raise ValueError("Only paid orders can be refunded.")


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="order_items"
    )
    quantity = models.PositiveIntegerField()
    price_per_item = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    class Meta:
        ordering = ["order"]
        verbose_name = "Order Item"
        verbose_name_plural = "Order Items"
        constraints = [
            models.CheckConstraint(
                check=models.Q(quantity__gte=1), name="quantity_non_negative"
            )
        ]

    def __str__(self):
        return f"{self.quantity} of {self.product.name} for Order {self.order.id}"

    def save(self, *args, **kwargs):
        self.total_price = self.quantity * self.price_per_item
        super().save(*args, **kwargs)

    def calculate_total_price(self):
        """Calculate the total price for this item."""
        self.total_price = self.quantity * self.price_per_item
        self.save(update_fields=["total_price"])


class Payment(models.Model):
    order = models.OneToOneField(
        Order, on_delete=models.CASCADE, related_name="payment"
    )
    payment_method = models.CharField(
        max_length=50,
        choices=[
            ("credit_card", "Credit Card"),
            ("paypal", "PayPal"),
            ("cash_on_delivery", "Cash on Delivery"),
        ],
    )
    payment_date = models.DateTimeField(null=True, blank=True)
    payment_status = models.CharField(
        max_length=50,
        choices=[
            ("paid", "Paid"),
            ("pending", "Pending"),
            ("failed", "Failed"),
        ],
        default="pending",
    )

    class Meta:
        ordering = ["-payment_date"]
        verbose_name = "Payment"
        verbose_name_plural = "Payments"

    def __str__(self):
        return f"Payment for Order {self.order.id} - {self.payment_status}"

    def process_payment(self, method):
        """Process the payment and mark it as 'paid'."""
        if self.order.status == "canceled":
            raise ValueError("Cannot process payment for a canceled order.")
        self.payment_method = method
        self.payment_status = "paid"
        self.payment_date = timezone.now()
        self.save()

    def refund_payment(self):
        """Refund the payment if it's already marked as paid."""
        if self.payment_status != "paid":
            raise ValueError("Only paid payments can be refunded.")
        self.payment_status = "refunded"
        self.payment_date = timezone.now()
        self.save()
