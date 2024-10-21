# controllers/warehouse_controller.py
from source.apps.customers.services.warehouse_service import WarehouseService


class WarehouseController:
    @staticmethod
    def assign_manager_to_warehouse(warehouse_id, user):
        """Assign a new manager to a warehouse."""
        return WarehouseService.assign_manager(warehouse_id, user)
