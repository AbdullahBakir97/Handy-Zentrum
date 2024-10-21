from django.db.models import Sum

from .models import Order
from .services import RepairCalculationService


def generate_daily_report(shop=None):
    daily_totals = RepairCalculationService.calculate_daily_totals(shop)

    report = f"""
    Daily Report:
    Total Orders: {daily_totals['total_orders']}
    Total Price: {daily_totals['total_price']}
    Total Expenses: {daily_totals['total_expenses']}
    Total Profit: {daily_totals['total_profit']}

    Profit for Owner: {daily_totals['profit_owner']}
    Profit for Worker: {daily_totals['profit_worker']}

    Unpaid Orders Count: {daily_totals['unpaid_orders_count']}
    Total Unpaid Amount: {daily_totals['unpaid_total']}
    """

    return report


def generate_revenue_report(start_date, end_date):
    orders = Order.objects.filter(
        order_date__range=(start_date, end_date), payment_status="paid"
    )
    total_revenue = orders.aggregate(total=Sum("total_amount"))["total"]
    return {"total_revenue": total_revenue, "total_orders": orders.count()}


def customer_order_report(customer_id):
    orders = Order.objects.by_customer(customer_id)
    return {
        "customer_name": orders.first().customer.name if orders.exists() else None,
        "order_count": orders.count(),
        "total_spent": orders.aggregate(total=Sum("total_amount"))["total"],
    }
