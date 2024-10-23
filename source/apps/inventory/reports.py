from django.db.models import Count, Sum

from .models import InventoryItem, InventoryTransfer, StockAdjustment


def inventory_report():
    total_stock = InventoryItem.objects.aggregate(total_stock=Sum("quantity"))[
        "total_stock"
    ]
    low_stock_items = (
        InventoryItem.objects.annotate(total_quantity=Sum("quantity"))
        .filter(total_quantity__lt=10)
        .count()
    )

    return {
        "total_stock": total_stock,
        "low_stock_items": low_stock_items,
    }


def stock_adjustment_report():
    adjustments = StockAdjustment.objects.values("adjustment_type").annotate(
        total_quantity=Sum("quantity")
    )
    return adjustments


def transfer_report():
    return InventoryTransfer.objects.values("status").annotate(
        total_transfers=Count("id")
    )


def stock_summary():
    return InventoryItem.objects.values("product__name", "location__name").annotate(
        total_quantity=Sum("quantity")
    )


def warehouse_stock(warehouse_id):
    return (
        InventoryItem.objects.filter(location_id=warehouse_id)
        .values("product__name")
        .annotate(total_quantity=Sum("quantity"))
    )


def stock_adjustments_summary():
    return StockAdjustment.objects.values("adjustment_type").annotate(
        total_adjustments=Count("id")
    )
