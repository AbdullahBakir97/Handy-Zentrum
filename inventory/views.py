from django.shortcuts import render
from rest_framework import viewsets
from .models import Product, InventoryItem, Warehouse, StockAdjustment, InventoryTransfer
from .serializers import (
    ProductSerializer, InventoryItemSerializer, WarehouseSerializer, 
    StockAdjustmentSerializer, InventoryTransferSerializer
)
from .services import StockAdjustmentService, InventoryTransferService

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class WarehouseViewSet(viewsets.ModelViewSet):
    queryset = Warehouse.objects.all()
    serializer_class = WarehouseSerializer

class InventoryItemViewSet(viewsets.ModelViewSet):
    queryset = InventoryItem.objects.all()
    serializer_class = InventoryItemSerializer

class StockAdjustmentViewSet(viewsets.ModelViewSet):
    queryset = StockAdjustment.objects.all()
    serializer_class = StockAdjustmentSerializer
    
    def perform_create(self, serializer):
        # Integrating StockAdjustmentService for managing adjustments
        adjustment = serializer.save()
        StockAdjustmentService.adjust_stock(adjustment)

class InventoryTransferViewSet(viewsets.ModelViewSet):
    queryset = InventoryTransfer.objects.all()
    serializer_class = InventoryTransferSerializer

    def perform_create(self, serializer):
        # Use InventoryTransferService for managing inventory transfers
        transfer = serializer.save()
        InventoryTransferService.initiate_transfer(transfer)