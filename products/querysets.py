from django.db import models
from django.db.models import Count, Sum, Q

class ProductQuerySet(models.QuerySet):
    def in_stock(self):
        return self.filter(inventory_records__status='in_stock').distinct()
    
    def low_stock(self, threshold=10):
        return self.annotate(total_quantity=Sum('inventory_records__quantity')).filter(total_quantity__lt=threshold)
    
    def reserved(self):
        return self.filter(inventory_records__status='reserved')

    def sold(self):
        return self.filter(inventory_records__status='sold')

    def by_category(self, category_id):
        return self.filter(category_id=category_id)