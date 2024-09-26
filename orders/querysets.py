from django.db import models
from django.db.models import Count, Sum, Q

class OrderQuerySet(models.QuerySet):
    def pending(self):
        return self.filter(status='pending')

    def paid(self):
        return self.filter(payment_status='paid')

    def shipped(self):
        return self.filter(status='shipped')

    def by_customer(self, customer_id):
        return self.filter(customer_id=customer_id)

    def recent(self, days):
        recent_date = timezone.now() - timedelta(days=days)
        return self.filter(order_date__gte=recent_date)