from .querysets import OrderQuerySet

class OrderManager(models.Manager):
    def get_queryset(self):
        return OrderQuerySet(self.model, using=self._db)

    def pending(self):
        return self.get_queryset().pending()

    def shipped(self):
        return self.get_queryset().shipped()

    def by_customer(self, customer_id):
        return self.get_queryset().by_customer(customer_id)