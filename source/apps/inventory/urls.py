from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import (
    ProductViewSet,
    WarehouseViewSet,
    InventoryItemViewSet,
    StockAdjustmentViewSet,
    InventoryTransferViewSet,
)

router = DefaultRouter()
router.register(r"products", ProductViewSet)
router.register(r"warehouses", WarehouseViewSet)
router.register(r"inventory-items", InventoryItemViewSet)
router.register(r"stock-adjustments", StockAdjustmentViewSet)
router.register(r"inventory-transfers", InventoryTransferViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
