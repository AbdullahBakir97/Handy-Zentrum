from decimal import Decimal

from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone

from .models import Order, OrderItem, Payment, RepairOrder


class RepairOrderForm(forms.ModelForm):
    class Meta:
        model = RepairOrder
        fields = [
            "shop",
            "device_type",
            "device_name",
            "issue",
            "total_price",
            "expenses",
            "status",
            "details",
            "customer_name",
            "customer_contact",
            "payment_received",
            "payment_pending_reason",
            "completion_time",
        ]
        widgets = {
            "status": forms.Select(attrs={"class": "form-control"}),
            "total_price": forms.NumberInput(attrs={"min": 0}),
            "expenses": forms.NumberInput(attrs={"min": 0}),
            "details": forms.Textarea(attrs={"rows": 3}),
            "completion_time": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }

    def clean_total_price(self):
        total_price = self.cleaned_data.get("total_price")
        if total_price < Decimal("0.00"):
            raise ValidationError("Total price cannot be negative.")
        return total_price

    def clean_expenses(self):
        expenses = self.cleaned_data.get("expenses")
        if expenses < Decimal("0.00"):
            raise ValidationError("Expenses cannot be negative.")
        return expenses

    def clean_completion_time(self):
        completion_time = self.cleaned_data.get("completion_time")
        if completion_time and completion_time < timezone.now():
            raise ValidationError("Completion time cannot be in the past.")
        return completion_time

    def save(self, commit=True):
        repair_order = super().save(commit=False)
        repair_order.calculate_profit()  # Ensure profit is recalculated
        if commit:
            repair_order.save()
        return repair_order


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = [
            "customer",
            "status",
            "shipping_address",
            "total_amount",
            "payment_status",
        ]
        widgets = {
            "status": forms.Select(attrs={"class": "form-control"}),
            "shipping_address": forms.TextInput(attrs={"class": "form-control"}),
            "total_amount": forms.NumberInput(attrs={"min": 0}),
        }

    def clean_total_amount(self):
        total_amount = self.cleaned_data.get("total_amount")
        if total_amount < Decimal("0.00"):
            raise ValidationError("Total amount cannot be negative.")
        return total_amount

    def save(self, commit=True):
        order = super().save(commit=False)
        order.calculate_total()  # Recalculate total amount based on items
        if commit:
            order.save()
        return order

    def update_status(self, new_status):
        if new_status not in [
            "pending",
            "processed",
            "shipped",
            "delivered",
            "canceled",
        ]:
            raise ValidationError(f"Invalid status: {new_status}")
        self.instance.status = new_status
        self.instance.save()


class OrderItemForm(forms.ModelForm):
    class Meta:
        model = OrderItem
        fields = ["order", "product", "quantity", "price_per_item"]
        widgets = {
            "quantity": forms.NumberInput(attrs={"min": 1}),
            "price_per_item": forms.NumberInput(attrs={"min": 0}),
        }

    def clean_quantity(self):
        quantity = self.cleaned_data.get("quantity")
        if quantity < 1:
            raise ValidationError("Quantity must be at least 1.")
        return quantity

    def clean_price_per_item(self):
        price_per_item = self.cleaned_data.get("price_per_item")
        if price_per_item < Decimal("0.00"):
            raise ValidationError("Price per item cannot be negative.")
        return price_per_item

    def save(self, commit=True):
        order_item = super().save(commit=False)
        order_item.calculate_total_price()  # Ensure total price is recalculated
        if commit:
            order_item.save()
        return order_item


class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ["order", "payment_method", "payment_status", "payment_date"]
        widgets = {
            "payment_method": forms.Select(attrs={"class": "form-control"}),
            "payment_status": forms.Select(attrs={"class": "form-control"}),
            "payment_date": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }

    def clean_payment_status(self):
        payment_status = self.cleaned_data.get("payment_status")
        if payment_status not in ["paid", "pending", "failed"]:
            raise ValidationError(f"Invalid payment status: {payment_status}")
        return payment_status

    def process_payment(self):
        # payment_status = self.cleaned_data.get("payment_status")
        if self.instance.order.status == "canceled":
            raise ValidationError("Cannot process payment for a canceled order.")
        self.instance.payment_status = "paid"
        self.instance.payment_date = timezone.now()
        self.instance.save()

    def refund_payment(self):
        if self.instance.payment_status != "paid":
            raise ValidationError("Only paid payments can be refunded.")
        self.instance.payment_status = "refunded"
        self.instance.payment_date = timezone.now()
        self.instance.save()
