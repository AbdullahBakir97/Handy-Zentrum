from django.db import models
from django.db.models import Sum


class BrandQuerySet(models.QuerySet):
    def active(self):
        return self.filter(is_active=True)

    def search(self, query):
        return self.filter(name__icontains=query)


class CategoryQuerySet(models.QuerySet):
    def active(self):
        return self.filter(is_active=True)

    def top_level(self):
        return self.filter(parent__isnull=True)


class ProductQuerySet(models.QuerySet):
    def in_stock(self):
        return self.filter(inventory_records__status="in_stock").distinct()

    def low_stock(self, threshold=10):
        return self.annotate(total_quantity=Sum("inventory_records__quantity")).filter(
            total_quantity__lt=threshold
        )

    def reserved(self):
        return self.filter(inventory_records__status="reserved")

    def sold(self):
        return self.filter(inventory_records__status="sold")

    def by_category(self, category_id):
        return self.filter(category_id=category_id)

    def active(self):
        return self.filter(is_active=True)

    def on_sale(self):
        return self.filter(flag="Sale")

    def featured(self):
        return self.filter(flag="Feature")

    def new_arrivals(self):
        return self.filter(flag="New")

    def by_brand(self, brand_slug):
        return self.filter(brand__slug=brand_slug)

    def by_tag(self, tag_name):
        return self.filter(tags__name__in=[tag_name])


class ProductVariantQuerySet(models.QuerySet):
    def active(self):
        return self.filter(is_active=True)

    def by_product(self, product):
        return self.filter(product=product)

    def in_stock(self):
        return self.filter(stock__gt=0)

    def within_price_range(self, min_price, max_price):
        return self.filter(price__gte=min_price, price__lte=max_price)


class ProductImageQuerySet(models.QuerySet):
    def by_product(self, product):
        return self.filter(product=product)
