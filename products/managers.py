from .querysets import ProductQuerySet
from django.db import models

class ProductManager(models.Manager):
    def get_queryset(self):
        return ProductQuerySet(self.model, using=self._db)

    def in_stock(self):
        return self.get_queryset().in_stock()
    
    def low_stock(self, threshold=10):
        return self.get_queryset().low_stock(threshold)
    
    def by_category(self, category):
        return self.get_queryset().by_category(category)