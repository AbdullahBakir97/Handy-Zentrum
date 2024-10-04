from django.db import models
from django.db.models import Count, Sum, Q


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
