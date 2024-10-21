from django.db import models
from django.contrib.auth.models import User
from django.forms import ValidationError
from source.apps.products.models import Product


class Warehouse(models.Model):
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    manager = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="warehouses_manager"
    )
    capacity = models.PositiveIntegerField(default=10000)

    class Meta:
        ordering = ["name"]
        verbose_name = "Warehouse"
        verbose_name_plural = "Warehouses"

    def __str__(self):
        return f"{self.name} - {self.location}"

    def total_stock(self):
        """Returns total quantity of products in the warehouse."""
        return (
            self.stocked_products.aggregate(total=models.Sum("quantity"))["total"] or 0
        )

    def generate_report(self):
        """Generate a warehouse-specific stock report."""
        # Implement report generation logic here
        pass


class InventoryItem(models.Model):
    STATUS_CHOICES = [
        ("in_stock", "In Stock"),
        ("reserved", "Reserved"),
        ("sold", "Sold"),
    ]
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="inventory_records"
    )
    quantity = models.IntegerField(default=0)
    location = models.ForeignKey(
        Warehouse, on_delete=models.CASCADE, related_name="stocked_products"
    )
    status = models.CharField(max_length=50, choices=STATUS_CHOICES)
    threshold = models.PositiveIntegerField(default=10)
    last_updated = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ("product", "location")
        ordering = ["-last_updated"]
        verbose_name = "Inventory Item"
        verbose_name_plural = "Inventory Items"

    def __str__(self):
        return f"{self.product.name} - {self.location.name} ({self.status})"

    def is_low_stock(self):
        """Checks if the inventory is low on stock based on a threshold."""
        return self.quantity < self.threshold

    def clean(self):
        """Ensure the status is valid."""
        if self.quantity == 0 and self.status != "sold":
            raise ValidationError(
                "An item with zero quantity should be marked as 'sold'."
            )

    def save(self, *args, **kwargs):
        """Update the last updated timestamp."""
        if self.quantity < 0:
            raise ValidationError("Quantity cannot be negative.")
        self.last_updated = models.DateTimeField(auto_now=True)
        super().save(*args, **kwargs)

    def delete(self):
        self.is_active = False
        self.save()


class StockAdjustment(models.Model):
    inventory_item = models.ForeignKey(
        InventoryItem, on_delete=models.CASCADE, related_name="stock_adjustments"
    )
    adjustment_type = models.CharField(
        max_length=50, choices=[("add", "Add"), ("remove", "Remove")]
    )
    quantity = models.IntegerField()
    reason = models.CharField(max_length=255, blank=True, null=True)
    performed_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="adjustments_performed"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Stock Adjustment"
        verbose_name_plural = "Stock Adjustments"

    def __str__(self):
        return f"{self.adjustment_type.capitalize()} {self.quantity} of {self.inventory_item.product.name}"

    def clean(self):
        """Validates that the adjustment type and quantity are appropriate."""
        if (
            self.adjustment_type == "remove"
            and self.inventory_item.quantity < self.quantity
        ):
            raise ValidationError("Cannot remove more items than available in stock.")
        if self.quantity <= 0:
            raise ValidationError("Adjustment quantity must be positive.")

    def save(self, *args, **kwargs):
        """Adjust inventory item quantity based on adjustment type."""
        if self.adjustment_type == "add":
            self.inventory_item.quantity += self.quantity
        elif self.adjustment_type == "remove":
            if self.inventory_item.quantity < self.quantity:
                raise ValidationError("Not enough stock to remove.")
            self.inventory_item.quantity -= self.quantity
        self.inventory_item.save()
        super().save(*args, **kwargs)


class InventoryTransfer(models.Model):
    TRANSFER_STATUS = [
        ("pending", "Pending"),
        ("completed", "Completed"),
        ("failed", "Failed"),
    ]
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="transfers_handled"
    )
    from_location = models.ForeignKey(
        Warehouse, related_name="outgoing_transfers", on_delete=models.CASCADE
    )
    to_location = models.ForeignKey(
        Warehouse, related_name="incoming_transfers", on_delete=models.CASCADE
    )
    quantity = models.IntegerField()
    reason = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=50, choices=TRANSFER_STATUS)
    expected_transfer_date = models.DateField(blank=True, null=True)
    initiated_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="transfers_initiated"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Inventory Transfer"
        verbose_name_plural = "Inventory Transfers"

    def __str__(self):
        return f"Transfer {self.product.name} from {self.from_location.name} to {self.to_location.name}"

    def is_transfer_possible(self):
        """Check if transfer is possible based on stock availability."""
        inventory_item = InventoryItem.objects.filter(
            product=self.product, location=self.from_location
        ).first()
        if inventory_item and inventory_item.quantity >= self.quantity:
            return True
        return False

    def clean(self):
        """Ensure stock is available before the transfer."""
        if not self.is_transfer_possible():
            raise ValidationError(
                "Not enough stock available in the source warehouse for transfer."
            )
        if self.from_location == self.to_location:
            raise ValidationError(
                "Source and destination warehouses cannot be the same."
            )

    def save(self, *args, **kwargs):
        """Handle the transfer logic based on status."""
        if not self.pk:
            # New transfer
            if self.status == "completed":
                # Deduct from source
                source_inventory = InventoryItem.objects.filter(
                    product=self.product, location=self.from_location
                ).first()
                if source_inventory and source_inventory.quantity >= self.quantity:
                    source_inventory.quantity -= self.quantity
                    source_inventory.save()
                else:
                    raise ValidationError("Insufficient stock in source warehouse.")

                # Add to destination
                dest_inventory, created = InventoryItem.objects.get_or_create(
                    product=self.product,
                    location=self.to_location,
                    defaults={"quantity": 0, "status": "in_stock"},
                )
                dest_inventory.quantity += self.quantity
                dest_inventory.save()
            super().save(*args, **kwargs)
        else:
            # Existing transfer
            previous = InventoryTransfer.objects.get(pk=self.pk)
            if previous.status != self.status:
                if self.status == "completed" and previous.status != "completed":
                    # Handle completion
                    if self.is_transfer_possible():
                        source_inventory = InventoryItem.objects.filter(
                            product=self.product, location=self.from_location
                        ).first()
                        dest_inventory, created = InventoryItem.objects.get_or_create(
                            product=self.product,
                            location=self.to_location,
                            defaults={"quantity": 0, "status": "in_stock"},
                        )
                        source_inventory.quantity -= self.quantity
                        source_inventory.save()
                        dest_inventory.quantity += self.quantity
                        dest_inventory.save()
                    else:
                        raise ValidationError(
                            "Not enough stock in source warehouse to complete transfer."
                        )
                elif self.status == "failed" and previous.status == "completed":
                    # Reverse the transfer
                    source_inventory = InventoryItem.objects.filter(
                        product=self.product, location=self.from_location
                    ).first()
                    dest_inventory = InventoryItem.objects.filter(
                        product=self.product, location=self.to_location
                    ).first()
                    if dest_inventory and dest_inventory.quantity >= self.quantity:
                        dest_inventory.quantity -= self.quantity
                        dest_inventory.save()
                        source_inventory.quantity += self.quantity
                        source_inventory.save()
                    else:
                        raise ValidationError(
                            "Cannot reverse transfer due to insufficient stock in destination warehouse."
                        )
            super().save(*args, **kwargs)
