from decimal import Decimal

from django.core.cache import cache
from django.db.models import Sum
from django.utils import timezone

from source.apps.inventory.services import InventoryService
from source.apps.logistics.models import Shipment

from .models import Order, Payment, RepairOrder
from .utils import (
    allocate_inventory,
    apply_payment_discount,
    calculate_shipping_cost,
    check_inventory_availability,
    format_order_summary,
    generate_order_report,
    is_order_cancelable,
    send_order_cancellation_alert,
    send_order_confirmation,
    send_order_shipment_notification,
    validate_payment_details,
)


class RepairCalculationService:
    @staticmethod
    def calculate_daily_totals(shop=None):
        """Calculate daily totals for the given shop or for all shops."""
        orders = RepairOrder.objects.filter(created_at__date=timezone.now().date())

        if shop:
            orders = orders.filter(shop=shop)

        # Calculate total prices, expenses, profits
        total_price = orders.aggregate(total_price=Sum("total_price"))[
            "total_price"
        ] or Decimal("0.00")
        total_expenses = orders.aggregate(total_expenses=Sum("expenses"))[
            "total_expenses"
        ] or Decimal("0.00")
        total_profit = total_price - total_expenses

        # Filter out unpaid orders using the manager's method
        unpaid_orders = RepairOrder.objects.unpaid_orders()  # Use the manager method
        unpaid_orders_count = unpaid_orders.count()
        unpaid_total = unpaid_orders.aggregate(unpaid_total=Sum("total_price"))[
            "unpaid_total"
        ] or Decimal("0.00")

        # Calculate profit splitting
        profit_owner = total_profit / 2
        profit_worker = total_profit / 2

        return {
            "total_orders": orders.count(),
            "total_price": total_price,
            "total_expenses": total_expenses,
            "total_profit": total_profit,
            "profit_owner": profit_owner,
            "profit_worker": profit_worker,
            "unpaid_orders_count": unpaid_orders_count,
            "unpaid_total": unpaid_total,
        }

    @staticmethod
    def verify_calculations():
        """Check that total_price - total_expenses equals total_profit."""
        daily_totals = RepairCalculationService.calculate_daily_totals()
        total_price = daily_totals["total_price"]
        total_expenses = daily_totals["total_expenses"]
        total_profit = daily_totals["total_profit"]

        return (total_price - total_expenses) == total_profit


class OrderService:
    @staticmethod
    def create_order(customer_id, order_data):
        """Creates a new order for the customer."""
        from source.apps.customers.models import Customer

        customer = Customer.objects.get(id=customer_id)
        order = Order.objects.create(customer=customer, **order_data)
        order.save()
        return order

    @staticmethod
    def get_order_details(order_id):
        """Fetches the details of an order."""
        return Order.objects.prefetch_related("items").get(id=order_id)

    @staticmethod
    def cancel_order(order_id):
        """Cancels the order and adjusts inventory if applicable."""
        order = Order.objects.get(id=order_id)
        if not is_order_cancelable(order.status):
            raise ValueError("Order cannot be canceled.")
        order.cancel_order()
        InventoryService.adjust_inventory_after_order(order_id)

    @staticmethod
    def update_order_status(order_id, new_status):
        """Updates the status of an order."""
        order = Order.objects.get(id=order_id)
        order.update_status(new_status)

    @staticmethod
    def apply_order_discount(order_id, discount_code):
        """Applies a discount to the order."""
        order = Order.objects.get(id=order_id)
        apply_payment_discount(order, discount_code)

    @staticmethod
    def get_order_history(customer_id):
        """Fetches the order history of a customer."""
        return Order.objects.filter(customer_id=customer_id).order_by("-order_date")


class PaymentService:
    @staticmethod
    def process_payment(order_id, payment_method):
        """Processes the payment for the given order."""
        order = Order.objects.get(id=order_id)
        payment = Payment.objects.create(order=order, payment_method=payment_method)
        # Simulate payment processing (e.g., via external payment gateways)
        payment.payment_status = "paid"
        payment.payment_date = timezone.now()
        payment.save()
        order.payment_status = "paid"
        order.save()

    @staticmethod
    def refund_payment(order_id):
        """Refunds the payment for the given order."""
        order = Order.objects.get(id=order_id)
        if order.payment_status != "paid":
            raise ValueError("Cannot refund an unpaid order.")
        order.refund()

    @staticmethod
    def validate_payment_method(payment_data):
        """Validates and applies payment method details."""
        validate_payment_details(payment_data)
        return True


class ShippingService:
    @staticmethod
    def create_shipment(order_id, shipping_address, shipping_method):
        """Creates a shipment for the given order."""
        order = Order.objects.get(id=order_id)
        shipment = Shipment.objects.create(
            order=order,
            shipping_address=shipping_address,
            shipping_method=shipping_method,
        )
        shipment.save()
        return shipment

    @staticmethod
    def track_shipment(order_id):
        """Tracks the shipment for the given order."""
        order = Order.objects.get(id=order_id)
        return order.shipment.get_tracking_info()

    @staticmethod
    def calculate_shipping(order_items, destination):
        """Calculates the shipping cost."""
        return calculate_shipping_cost(order_items, destination)

    @staticmethod
    def cancel_shipment(shipment_id):
        """Cancels a shipment."""
        shipment = Shipment.objects.get(id=shipment_id)
        shipment.cancel_shipment()


class FulfillmentService:
    @staticmethod
    def process_order_fulfillment(order_id):
        """Processes order fulfillment by allocating inventory and preparing shipment."""
        order = Order.objects.get(id=order_id)
        check_inventory_availability(order.items)
        allocate_inventory(order.items)
        ShippingService.create_shipment(order.id, order.shipping_address, "standard")

    @staticmethod
    def update_fulfillment_status(order_id, status):
        """Updates the fulfillment status of an order."""
        order = Order.objects.get(id=order_id)
        order.update_fulfillment_status(status)


class NotificationService:
    @staticmethod
    def send_order_notifications(order):
        """Sends relevant notifications for order placement, shipment, and cancellation."""
        if order.status == "placed":
            send_order_confirmation(order)
        elif order.status == "shipped":
            send_order_shipment_notification(order)
        elif order.status == "canceled":
            send_order_cancellation_alert(order)


class ReportingService:
    @staticmethod
    def generate_order_report(order_id):
        """Generates a detailed report for the given order."""
        order = Order.objects.get(id=order_id)
        return generate_order_report(order)

    @staticmethod
    def generate_sales_report(start_date, end_date):
        """Generates a sales report for a given date range."""
        from source.apps.orders.models import Order

        orders = Order.objects.filter(order_date__range=(start_date, end_date))
        total_sales = sum(order.total_amount for order in orders)
        return {"total_orders": orders.count(), "total_sales": total_sales}


class CachingService:
    @staticmethod
    def cache_order_data(order):
        """Caches order data for faster retrieval."""
        cache_key = f"order_{order.id}"
        cache.set(cache_key, format_order_summary(order), timeout=3600)

    @staticmethod
    def get_cached_order_data(order_id):
        """Retrieves cached order data."""
        cache_key = f"order_{order_id}"
        return cache.get(cache_key)

    @staticmethod
    def invalidate_cache(order_id):
        """Invalidates the cache for a specific order."""
        cache_key = f"order_{order_id}"
        cache.delete(cache_key)
