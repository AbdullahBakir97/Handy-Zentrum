import re
from .models import Customer, LoyaltyProgram

def format_phone_number(phone_number):
    """Format phone number to international format."""
    return re.sub(r'\D', '', phone_number)

def is_valid_email(email):
    """Check if email is valid."""
    return bool(re.match(r"[^@]+@[^@]+\.[^@]+", email))

def calculate_loyalty_tier(points):
    if points > 1000:
        return 'gold'
    elif points > 500:
        return 'silver'
    return 'bronze'

def check_and_upgrade_loyalty_tier(customer):
    """Check the customer's loyalty points and upgrade their tier if necessary."""
    if customer.is_loyalty_member:
        new_tier = calculate_loyalty_tier(customer.loyalty_program.points)
        if customer.loyalty_program.tier != new_tier:
            customer.loyalty_program.tier = new_tier
            customer.loyalty_program.save()

def add_loyalty_points(customer, points):
    if customer.is_loyalty_member:
        customer.loyalty_program.points += points
        check_and_upgrade_loyalty_tier(customer)
        customer.loyalty_program.save()

def remove_loyalty_points(customer, points):
    if customer.is_loyalty_member and customer.loyalty_program.points >= points:
        customer.loyalty_program.points -= points
        check_and_upgrade_loyalty_tier(customer)
        customer.loyalty_program.save()

def segment_customers_by_tier():
    tiers = {
        'bronze': Customer.objects.filter(loyalty_program__tier='bronze'),
        'silver': Customer.objects.filter(loyalty_program__tier='silver'),
        'gold': Customer.objects.filter(loyalty_program__tier='gold'),
    }
    return tiers

def bulk_import_customers(customer_data):
    customers = []
    for data in customer_data:
        customer = Customer(
            first_name=data['first_name'],
            last_name=data['last_name'],
            email=data['email'],
            phone_number=data['phone_number'],
            address=data.get('address', ''),
            city=data.get('city', ''),
            country=data.get('country', ''),
            is_loyalty_member=data.get('is_loyalty_member', False)
        )
        customer.save()
        customers.append(customer)
    return customers

def export_customers_to_csv(queryset):
    import csv
    from django.http import HttpResponse

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="customers.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['First Name', 'Last Name', 'Email', 'Phone Number', 'Loyalty Points'])
    
    for customer in queryset:
        writer.writerow([customer.first_name, customer.last_name, customer.email, customer.phone_number, customer.loyalty_program.points])

    return response
