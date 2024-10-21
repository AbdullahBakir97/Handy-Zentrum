from django.urls import include, path
from rest_framework.routers import DefaultRouter

from source.apps.products.views import ProductViewSet

from .views import (
    InventoryItemViewSet,
    InventoryTransferViewSet,
    StockAdjustmentViewSet,
    WarehouseViewSet,
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
