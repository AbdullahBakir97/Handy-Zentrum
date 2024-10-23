from .models import InventoryItem, InventoryTransfer, StockAdjustment


class InventoryService:
    @staticmethod
    def add_stock(product, warehouse, quantity):
        item, created = InventoryItem.objects.get_or_create(
            product=product, location=warehouse
        )
        item.quantity += quantity
        item.status = "in_stock"
        item.save()
        return item

    @staticmethod
    def remove_stock(product, warehouse, quantity):
        item = InventoryItem.objects.get(product=product, location=warehouse)
        if item.quantity >= quantity:
            item.quantity -= quantity
            if item.quantity == 0:
                item.status = "sold"
            item.save()
        else:
            raise ValueError("Insufficient stock")
        return item


class StockAdjustmentService:
    @staticmethod
    def create_adjustment(inventory_item, adjustment_type, quantity, reason, user):
        adjustment = StockAdjustment.objects.create(
            inventory_item=inventory_item,
            adjustment_type=adjustment_type,
            quantity=quantity,
            reason=reason,
            performed_by=user,
        )
        if adjustment_type == "add":
            inventory_item.quantity += quantity
        elif adjustment_type == "remove" and inventory_item.quantity >= quantity:
            inventory_item.quantity -= quantity
        inventory_item.save()
        return adjustment

    @staticmethod
    def adjust_stock(inventory_item, adjustment_type, quantity, reason, user):
        if adjustment_type == "add":
            inventory_item.quantity += quantity
        elif adjustment_type == "remove" and inventory_item.quantity >= quantity:
            inventory_item.quantity -= quantity
        inventory_item.save()

        StockAdjustment.objects.create(
            inventory_item=inventory_item,
            adjustment_type=adjustment_type,
            quantity=quantity,
            reason=reason,
            performed_by=user,
        )


class TransferService:
    @staticmethod
    def initiate_transfer(product, from_location, to_location, quantity, user):
        transfer = InventoryTransfer.objects.create(
            product=product,
            from_location=from_location,
            to_location=to_location,
            quantity=quantity,
            initiated_by=user,
            status="pending",
        )
        return transfer

    @staticmethod
    def complete_transfer(transfer):
        transfer.status = "completed"
        transfer.save()
        return transfer

    @staticmethod
    def transfer_stock(product, from_warehouse, to_warehouse, quantity, user):
        if InventoryItem.objects.filter(
            product=product, location=from_warehouse, quantity__gte=quantity
        ).exists():
            inventory_item = InventoryItem.objects.get(
                product=product, location=from_warehouse
            )
            StockAdjustmentService.adjust_stock(
                inventory_item,
                "remove",
                quantity,
                "Transfer to another warehouse",
                user,
            )

            to_inventory_item, _ = InventoryItem.objects.get_or_create(
                product=product, location=to_warehouse
            )
            StockAdjustmentService.adjust_stock(
                to_inventory_item, "add", quantity, "Received from transfer", user
            )

            InventoryTransfer.objects.create(
                product=product,
                from_location=from_warehouse,
                to_location=to_warehouse,
                quantity=quantity,
                initiated_by=user,
                status="completed",
            )
