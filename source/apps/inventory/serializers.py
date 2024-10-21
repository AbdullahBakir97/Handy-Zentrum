from rest_framework import serializers
from .models import Warehouse, InventoryItem, StockAdjustment, InventoryTransfer


class WarehouseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Warehouse
        fields = ["id", "name", "location", "manager"]


class InventoryItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)
    location_name = serializers.CharField(source="location.name", read_only=True)

    class Meta:
        model = InventoryItem
        fields = [
            "id",
            "product",
            "product_name",
            "quantity",
            "location",
            "location_name",
            "status",
            "last_updated",
        ]


class StockAdjustmentSerializer(serializers.ModelSerializer):
    inventory_item_details = InventoryItemSerializer(
        source="inventory_item", read_only=True
    )

    class Meta:
        model = StockAdjustment
        fields = [
            "id",
            "inventory_item",
            "inventory_item_details",
            "adjustment_type",
            "quantity",
            "reason",
            "performed_by",
            "created_at",
        ]


class InventoryTransferSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)
    from_location_name = serializers.CharField(
        source="from_location.name", read_only=True
    )
    to_location_name = serializers.CharField(source="to_location.name", read_only=True)

    class Meta:
        model = InventoryTransfer
        fields = [
            "id",
            "product",
            "product_name",
            "from_location",
            "from_location_name",
            "to_location",
            "to_location_name",
            "quantity",
            "initiated_by",
            "created_at",
            "status",
        ]
