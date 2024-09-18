from django.db import models
from .querysets import CustomerQuerySet

class CustomerManager(models.Manager):
    def get_queryset(self):
        return CustomerQuerySet(self.model, using=self._db)

    def by_loyalty_tier(self, tier):
        return self.get_queryset().by_loyalty_tier(tier)

    def active_customers(self):
        return self.get_queryset().active_customers()

    def inactive_customers(self):
        return self.get_queryset().inactive_customers()

    def top_customers(self):
        return self.get_queryset().top_customers_by_loyalty_points()
