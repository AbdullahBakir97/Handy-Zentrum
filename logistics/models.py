from django.db import models
from inventory.models import Product, Warehouse

class Shipment(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='shipments')
    quantity = models.IntegerField()
    origin = models.ForeignKey(Warehouse, related_name='outgoing_shipments', on_delete=models.CASCADE)
    destination = models.CharField(max_length=255)
    shipped_date = models.DateTimeField()
    estimated_arrival = models.DateTimeField()
    tracking_number = models.CharField(max_length=255, unique=True)
    shipping_company = models.CharField(max_length=255, default='DHL')
    status = models.CharField(max_length=50, choices=[
        ('pending', 'Pending'),
        ('in_transit', 'In Transit'),
        ('delivered', 'Delivered'),
        ('returned', 'Returned'),
    ], default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Shipment {self.tracking_number} - {self.status}'
    
class LogisticsInteraction(models.Model):
    shipment = models.ForeignKey(Shipment, on_delete=models.CASCADE, related_name='logistics_interactions')
    interaction_type = models.CharField(max_length=50, choices=[
        ('pickup', 'Pickup'),
        ('delivered', 'Delivered'),
        ('delay', 'Delay'),
        ('customs', 'Customs Clearance'),
    ])
    timestamp = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f'{self.interaction_type} for {self.shipment.tracking_number}'
    
class ReturnShipment(models.Model):
    shipment = models.OneToOneField(Shipment, on_delete=models.CASCADE, related_name='return_details')
    reason = models.TextField(blank=True, null=True)
    received_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=50, choices=[
        ('initiated', 'Initiated'),
        ('in_transit', 'In Transit'),
        ('received', 'Received'),
        ('refunded', 'Refunded'),
    ], default='initiated')

    def __str__(self):
        return f'Return for {self.shipment.tracking_number}'
