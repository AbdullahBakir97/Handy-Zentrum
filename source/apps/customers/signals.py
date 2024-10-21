from django.db.models.signals import post_save, pre_save, pre_delete
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Customer, CustomerInteraction, LoyaltyProgram
from django.core.mail import send_mail
from .helpers.utils import calculate_loyalty_tier


@receiver(post_save, sender=User)
def create_customer_for_new_user(sender, instance, created, **kwargs):
    """Automatically create a Customer when a new User is registered."""
    if created:
        # Check if a customer already exists for this user (edge case)
        if not Customer.objects.filter(user=instance).exists():
            Customer.objects.create(
                user=instance,
                first_name=instance.first_name,
                last_name=instance.last_name,
                email=instance.email,
                phone_number="",  # You can update this if you have a phone number field on User
            )


@receiver(post_save, sender=Customer)
def sync_user_with_customer(sender, instance, **kwargs):
    """Ensure the associated User model reflects Customer details."""
    user = instance.user
    if (
        user.first_name != instance.first_name
        or user.last_name != instance.last_name
        or user.email != instance.email
    ):
        user.first_name = instance.first_name
        user.last_name = instance.last_name
        user.email = instance.email
        user.save()


@receiver(post_save, sender=User)
def sync_customer_with_user(sender, instance, **kwargs):
    """Update Customer details when User data changes."""
    try:
        customer = instance.customer_user
        if (
            customer.first_name != instance.first_name
            or customer.last_name != instance.last_name
            or customer.email != instance.email
        ):
            customer.first_name = instance.first_name
            customer.last_name = instance.last_name
            customer.email = instance.email
            customer.save()
    except Customer.DoesNotExist:
        # No customer associated with this user
        pass


@receiver(post_save, sender=CustomerInteraction)
def update_last_interaction(sender, instance, **kwargs):
    """Update a timestamp or other relevant data when a new interaction is logged."""
    instance.customer.last_interaction = instance.interaction_date
    instance.customer.save()


@receiver(post_save, sender=LoyaltyProgram)
def update_loyalty_status(sender, instance, **kwargs):
    """Update the customer's loyalty status when their program changes."""
    customer = instance.customer
    if instance.points >= 1000:
        customer.loyalty_tier_updated = "gold"
    elif instance.points >= 500:
        customer.loyalty_tier_updated = "silver"
    else:
        customer.loyalty_tier_updated = "bronze"
    customer.save()


# Notify on Customer Interaction
@receiver(post_save, sender=CustomerInteraction)
def notify_staff_on_interaction(sender, instance, created, **kwargs):
    if created and instance.interaction_type == "complaint":
        send_mail(
            "New Customer Complaint",
            f"Customer {instance.customer} has submitted a complaint.",
            "from@example.com",
            ["staff@example.com"],
        )


# Handle User cleanup when Customer is deleted
@receiver(pre_delete, sender=Customer)
def delete_related_user(sender, instance, **kwargs):
    if instance.user:
        instance.user.delete()
