from .models import Product, Warehouse
from .services import InventoryService, StockAdjustmentService, TransferService


class LogisticsController:
    def adjust_stock(self, product_id, warehouse_id, adjustment_type, quantity, user):
        product = Product.objects.get(id=product_id)
        warehouse = Warehouse.objects.get(id=warehouse_id)
        inventory_item = (
            InventoryService.add_stock(product, warehouse, quantity)
            if adjustment_type == "add"
            else InventoryService.remove_stock(product, warehouse, quantity)
        )
        return StockAdjustmentService.create_adjustment(
            inventory_item, adjustment_type, quantity, "Manual Adjustment", user
        )

    def transfer_product(
        self, product_id, from_location_id, to_location_id, quantity, user
    ):
        product = Product.objects.get(id=product_id)
        from_location = Warehouse.objects.get(id=from_location_id)
        to_location = Warehouse.objects.get(id=to_location_id)
        transfer = TransferService.initiate_transfer(
            product, from_location, to_location, quantity, user
        )
        return transfer
