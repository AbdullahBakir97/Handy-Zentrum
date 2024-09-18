from .models import Customer, LoyaltyProgram
from django.db.models import Count, Avg

def customer_kpis():
    total_customers = Customer.objects.count()
    active_loyalty_members = Customer.objects.filter(is_loyalty_member=True).count()
    avg_loyalty_points = LoyaltyProgram.objects.aggregate(Avg('points'))['points__avg']
    
    return {
        'total_customers': total_customers,
        'active_loyalty_members': active_loyalty_members,
        'avg_loyalty_points': avg_loyalty_points,
    }

def loyalty_tier_distribution():
    return LoyaltyProgram.objects.values('tier').annotate(count=Count('tier'))

def interaction_report():
    return Customer.objects.annotate(interaction_count=Count('customer_interactions')).values('first_name', 'last_name', 'interaction_count').order_by('-interaction_count')

def customer_retention_report():
    from django.utils import timezone
    from datetime import timedelta
    one_year_ago = timezone.now() - timedelta(days=365)
    active_customers = Customer.objects.filter(customer_interactions__interaction_date__gte=one_year_ago).distinct()
    total_customers = Customer.objects.count()

    return {
        'retained_customers': active_customers.count(),
        'retention_rate': (active_customers.count() / total_customers) * 100 if total_customers else 0
    }

def inactive_customers_report():
    return Customer.objects.filter(customer_interactions__isnull=True).values('first_name', 'last_name', 'email')
