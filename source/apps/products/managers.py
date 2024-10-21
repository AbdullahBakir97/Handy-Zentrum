from .querysets import ProductQuerySet
from django.db import models


class BrandManager(models.Manager):
    def active(self):
        return self.filter(is_active=True)

    def search(self, query):
        return self.filter(name__icontains=query)


class CategoryManager(models.Manager):
    def active(self):
        return self.filter(is_active=True)

    def top_level(self):
        return self.filter(parent__isnull=True)


class ProductManager(models.Manager):
    def get_queryset(self):
        return ProductQuerySet(self.model, using=self._db)

    def in_stock(self):
        return self.get_queryset().in_stock()

    def low_stock(self, threshold=10):
        return self.get_queryset().low_stock(threshold)

    def by_category(self, category):
        return self.get_queryset().by_category(category)

    def active(self):
        return self.filter(is_active=True)

    def on_sale(self):
        return self.filter(flag="Sale")

    def featured(self):
        return self.filter(flag="Feature")

    def new_arrivals(self):
        return self.filter(flag="New")


class ProductVariantManager(models.Manager):
    def active(self):
        return self.filter(is_active=True)

    def by_product(self, product):
        return self.filter(product=product)

    def in_stock(self):
        return self.filter(stock__gt=0)


class ProductImageManager(models.Manager):
    def by_product(self, product):
        return self.filter(product=product)
