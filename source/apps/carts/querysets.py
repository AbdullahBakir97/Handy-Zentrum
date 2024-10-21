from datetime import timedelta

from django.db import models
from django.utils import timezone


class CartQuerySet(models.QuerySet):
    def active(self):
        return self.filter(is_active=True)

    def abandoned(self, days=30):
        cutoff_date = timezone.now() - timedelta(days=days)
        return self.filter(is_active=True, updated_at__lt=cutoff_date)

    def for_customer(self, customer):
        return self.filter(customer=customer)

    def with_total_over(self, amount):
        return self.filter(total_price__gt=amount)

    def recent(self):
        return self.order_by("-updated_at")

    def active_carts_with_items(self):
        return (
            self.filter(is_active=True)
            .annotate(item_count=models.Count("items"))
            .filter(item_count__gt=0)
        )
