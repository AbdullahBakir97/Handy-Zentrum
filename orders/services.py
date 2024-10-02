from .models import RepairOrder
from django.db.models import Sum
from decimal import Decimal
from django.utils import timezone

class RepairCalculationService:
    @staticmethod
    def calculate_daily_totals(shop=None):
        """Calculate daily totals for the given shop or for all shops."""
        orders = RepairOrder.objects.filter(created_at__date=timezone.now().date())

        if shop:
            orders = orders.filter(shop=shop)

        # Calculate total prices, expenses, profits
        total_price = orders.aggregate(total_price=Sum('total_price'))['total_price'] or Decimal('0.00')
        total_expenses = orders.aggregate(total_expenses=Sum('expenses'))['total_expenses'] or Decimal('0.00')
        total_profit = total_price - total_expenses

        # Filter out unpaid orders using the manager's method
        unpaid_orders = RepairOrder.objects.unpaid_orders()  # Use the manager method
        unpaid_orders_count = unpaid_orders.count()
        unpaid_total = unpaid_orders.aggregate(unpaid_total=Sum('total_price'))['unpaid_total'] or Decimal('0.00')

        # Calculate profit splitting
        profit_owner = total_profit / 2
        profit_worker = total_profit / 2

        return {
            'total_orders': orders.count(),
            'total_price': total_price,
            'total_expenses': total_expenses,
            'total_profit': total_profit,
            'profit_owner': profit_owner,
            'profit_worker': profit_worker,
            'unpaid_orders_count': unpaid_orders_count,
            'unpaid_total': unpaid_total,
        }

    @staticmethod
    def verify_calculations():
        """Check that total_price - total_expenses equals total_profit."""
        daily_totals = RepairCalculationService.calculate_daily_totals()
        total_price = daily_totals['total_price']
        total_expenses = daily_totals['total_expenses']
        total_profit = daily_totals['total_profit']

        return (total_price - total_expenses) == total_profit



