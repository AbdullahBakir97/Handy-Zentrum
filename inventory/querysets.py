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

class InventoryItemQuerySet(models.QuerySet):
    def by_status(self, status):
        return self.filter(status=status)
    
    def total_stock(self):
        return self.aggregate(Sum('quantity'))['quantity__sum'] or 0
    
    def stock_in_warehouse(self, warehouse):
        return self.filter(location=warehouse).aggregate(Sum('quantity'))['quantity__sum'] or 0

    def in_warehouse(self, warehouse_id):
        return self.filter(location_id=warehouse_id)

    def in_stock(self):
        return self.filter(status='in_stock')

    def reserved(self):
        return self.filter(status='reserved')

    def sold(self):
        return self.filter(status='sold')
    
class WarehouseQuerySet(models.QuerySet):
    def with_manager(self, user_id):
        return self.filter(manager_id=user_id)
