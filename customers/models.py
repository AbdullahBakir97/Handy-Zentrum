from django.db import models
from django.contrib.auth.models import User
from .managers import CustomerManager

class Customer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='customer_user')
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
        return f'{self.first_name} {self.last_name}'
    
    class Meta:
        ordering = ['-date_joined']
        verbose_name = 'Customer'
        verbose_name_plural = 'Customers'
    
class CustomerInteraction(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='customer_interactions')
    interaction_type = models.CharField(max_length=100, choices=[
        ('inquiry', 'Inquiry'),
        ('complaint', 'Complaint'),
        ('feedback', 'Feedback'),
    ])
    interaction_date = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f'{self.interaction_type} with {self.customer.first_name}'
    
    class Meta:
        ordering = ['-interaction_date']
        verbose_name = 'Customer Interaction'
        verbose_name_plural = 'Customer Interactions'
    
class Address(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='addresses')
    address_type = models.CharField(max_length=20, choices=[('billing', 'Billing'), ('shipping', 'Shipping')])
    address_line_1 = models.CharField(max_length=255)
    address_line_2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    
    def __str__(self):
        return f'{self.address_type} Address for {self.customer}'

    class Meta:
        verbose_name = 'Address'
        verbose_name_plural = 'Addresses'
        
class LoyaltyProgram(models.Model):
    customer = models.OneToOneField(Customer, on_delete=models.CASCADE, related_name='loyalty_program')
    points = models.PositiveIntegerField(default=0)
    tier = models.CharField(max_length=50, choices=[
        ('bronze', 'Bronze'),
        ('silver', 'Silver'),
        ('gold', 'Gold'),
    ], default='bronze')

    def __str__(self):
        return f'{self.customer.first_name} - {self.tier} Member'
    
    class Meta:
        verbose_name = 'Loyalty Program'
        verbose_name_plural = 'Loyalty Programs'

