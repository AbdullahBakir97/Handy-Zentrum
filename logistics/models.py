from django.db import models
from inventory.models import Product, Warehouse
from .settings import LOGISTICS_SETTINGS

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
        (status, status.capitalize()) for status in LOGISTICS_SETTINGS['SHIPMENT_STATUSES']
    ], default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-shipped_date']
        verbose_name = 'Shipment'
        verbose_name_plural = 'Shipments'

    def __str__(self):
        return f'Shipment {self.tracking_number} - Status: {self.status}'

    def clean(self):
        """Ensure shipment data is valid."""
        if self.quantity <= 0:
            raise ValidationError("Shipment quantity must be a positive number.")
        if self.estimated_arrival <= self.shipped_date:
            raise ValidationError("Estimated arrival must be after the shipped date.")

    def is_delayed(self):
        """Check if the shipment is delayed."""
        return self.status != 'delivered' and self.estimated_arrival < timezone.now()

    def days_until_arrival(self):
        """Calculate the number of days until the shipment's estimated arrival."""
        return (self.estimated_arrival - timezone.now()).days

    
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

    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Logistics Interaction'
        verbose_name_plural = 'Logistics Interactions'

    def __str__(self):
        return f'{self.interaction_type.capitalize()} for {self.shipment.tracking_number} on {self.timestamp}'

    def log_interaction(self, interaction_type, notes=None):
        """Log a new interaction for this shipment."""
        LogisticsInteraction.objects.create(
            shipment=self.shipment,
            interaction_type=interaction_type,
            notes=notes
        )


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

    class Meta:
        ordering = ['-received_at']
        verbose_name = 'Return Shipment'
        verbose_name_plural = 'Return Shipments'

    def __str__(self):
        return f'Return for {self.shipment.tracking_number} - Status: {self.status}'

    def clean(self):
        """Ensure that received_at is set only when status is 'received'."""
        if self.status == 'received' and not self.received_at:
            raise ValidationError("Received date must be set when the return status is 'received'.")
        if self.status != 'received' and self.received_at:
            raise ValidationError("Received date can only be set when the return is marked as 'received'.")

    def is_return_refunded(self):
        """Check if the return shipment is fully refunded."""
        return self.status == 'refunded'

    def mark_as_received(self, received_at=None):
        """Mark the return shipment as received and set the received date."""
        self.status = 'received'
        self.received_at = received_at or timezone.now()
        self.save()
