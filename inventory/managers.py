from .querysets import ProductQuerySet, InventoryItemQuerySet, WarehouseQuerySet
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

class InventoryItemManager(models.Manager):
    def get_queryset(self):
        return InventoryItemQuerySet(self.model, using=self._db)

    def by_status(self, status):
        return self.get_queryset().by_status(status)
    
    def total_stock(self):
        return self.get_queryset().total_stock()

    def stock_in_warehouse(self, warehouse):
        return self.get_queryset().stock_in_warehouse(warehouse)
    
    def in_warehouse(self, warehouse_id):
        return self.get_queryset().in_warehouse(warehouse_id)
    
class WarehouseManager(models.Manager):
    def get_queryset(self):
        return WarehouseQuerySet(self.model, using=self._db)

    def with_manager(self, user_id):
        return self.get_queryset().with_manager(user_id)
