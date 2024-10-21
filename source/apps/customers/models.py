from datetime import timedelta, timezone
from django.db import models
from django.contrib.auth.models import User
from .managers import CustomerManager


class Customer(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="customer_user"
    )
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, unique=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    is_loyalty_member = models.BooleanField(default=False)
    loyalty_points = models.PositiveIntegerField(default=0)
    loyalty_tier_updated = models.DateTimeField(auto_now=True)
    objects = CustomerManager

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        ordering = ["-date_joined"]
        verbose_name = "Customer"
        verbose_name_plural = "Customers"
        constraints = [
            models.UniqueConstraint(fields=["email"], name="unique_email"),
            models.UniqueConstraint(
                fields=["phone_number"], name="unique_phone_number"
            ),
        ]

    def update_loyalty_points(self, points):
        """Update loyalty points and adjust membership status."""
        self.loyalty_points += points
        self.is_loyalty_member = self.loyalty_points > 0
        self.save()

    def get_full_name(self):
        """Return the full name of the customer."""
        return f"{self.first_name} {self.last_name}"


class CustomerInteraction(models.Model):
    customer = models.ForeignKey(
        Customer, on_delete=models.CASCADE, related_name="customer_interactions"
    )
    interaction_type = models.CharField(
        max_length=100,
        choices=[
            ("inquiry", "Inquiry"),
            ("complaint", "Complaint"),
            ("feedback", "Feedback"),
        ],
    )
    interaction_date = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.interaction_type} with {self.customer.first_name}"

    class Meta:
        ordering = ["-interaction_date"]
        verbose_name = "Customer Interaction"
        verbose_name_plural = "Customer Interactions"

    def was_recent(self):
        """Check if the interaction was within the last 30 days."""
        return self.interaction_date >= timezone.now() - timedelta(days=30)


class Address(models.Model):
    customer = models.ForeignKey(
        Customer, on_delete=models.CASCADE, related_name="addresses"
    )
    address_type = models.CharField(
        max_length=20, choices=[("billing", "Billing"), ("shipping", "Shipping")]
    )
    address_line_1 = models.CharField(max_length=255)
    address_line_2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.address_type} Address for {self.customer}"

    class Meta:
        verbose_name = "Address"
        verbose_name_plural = "Addresses"
        unique_together = ("customer", "address_type")

    def is_complete(self):
        """Check if the address has all required fields."""
        return all([self.address_line_1, self.city, self.country, self.postal_code])


class LoyaltyProgram(models.Model):
    customer = models.OneToOneField(
        Customer, on_delete=models.CASCADE, related_name="loyalty_program"
    )
    points = models.PositiveIntegerField(default=0)
    tier = models.CharField(
        max_length=50,
        choices=[
            ("bronze", "Bronze"),
            ("silver", "Silver"),
            ("gold", "Gold"),
        ],
        default="bronze",
    )

    def __str__(self):
        return f"{self.customer.first_name} - {self.tier} Member"

    class Meta:
        verbose_name = "Loyalty Program"
        verbose_name_plural = "Loyalty Programs"

    def update_tier(self):
        """Update loyalty tier based on points."""
        if self.points < 100:
            self.tier = "bronze"
        elif self.points < 500:
            self.tier = "silver"
        else:
            self.tier = "gold"
        self.save()
