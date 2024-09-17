from django.db import models
from django.contrib.auth.models import User


class Customer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='users')
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, unique=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    is_loyalty_member = models.BooleanField(default=False)
    loyalty_points = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'
    
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
