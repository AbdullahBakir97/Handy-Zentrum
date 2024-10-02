from .querysets import OrderQuerySet, RepairOrderQuerySet
from django.db import models
from django.utils import timezone

class OrderManager(models.Manager):
    def get_queryset(self):
        return OrderQuerySet(self.model, using=self._db)

    def pending(self):
        return self.get_queryset().pending()

    def shipped(self):
        return self.get_queryset().shipped()

    def by_customer(self, customer_id):
        return self.get_queryset().by_customer(customer_id)
    
class RepairOrderManager(models.Manager):
    def get_queryset(self):
        return RepairOrderQuerySet(self.model, using=self._db)
        
    def created_today(self):
        return self.get_queryset().created_today()

    def daily_report(self):
        return self.get_queryset().created_today().total_calculations()
    
    def unpaid_orders(self):
        return self.filter(payment_received=False)

    def unpaid_customer_orders(self):
        """Orders awaiting customer pickup."""
        return self.filter(payment_received=False, payment_pending_reason="Awaiting Customer Pickup")

    def unpaid_shop_orders(self):
        """Orders awaiting payment from another shop."""
        return self.filter(payment_received=False, payment_pending_reason="Sent to Other Shop")

    def completed_orders(self):
        """Orders marked as completed (paid or unpaid)."""
        return self.filter(status__in=['completed', 'customer_pickup', 'sent_to_other_shop'])

