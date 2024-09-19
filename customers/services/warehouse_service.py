# services/warehouse_service.py

from .models import Warehouse

class WarehouseService:
    @staticmethod
    def assign_manager(warehouse_id, user):
        """Assigns a new manager to the warehouse."""
        warehouse = Warehouse.objects.get(id=warehouse_id)
        warehouse.manager = user
        warehouse.save()
        return warehouse
