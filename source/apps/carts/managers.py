from django.db import models

from .querysets import CartQuerySet


class CartManager(models.Manager):
    def get_queryset(self):
        return CartQuerySet(self.model, using=self._db)

    def active(self):
        return self.get_queryset().active()

    def abandoned(self, days=30):
        return self.get_queryset().abandoned(days=days)

    def for_customer(self, customer):
        return self.get_queryset().for_customer(customer)

    def with_total_over(self, amount):
        return self.get_queryset().with_total_over(amount)

    def recent(self):
        return self.get_queryset().recent()

    def active_carts_with_items(self):
        return self.get_queryset().active_carts_with_items()
