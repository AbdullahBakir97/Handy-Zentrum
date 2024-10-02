from django.db import models
from django.db.models import Count, Sum, Q
from django.utils import timezone
from datetime import timedelta

class OrderQuerySet(models.QuerySet):
    def pending(self):
        return self.filter(status='pending')

    def paid(self):
        return self.filter(payment_status='paid')

    def shipped(self):
        return self.filter(status='shipped')

    def by_customer(self, customer_id):
        return self.filter(customer_id=customer_id)

    def recent(self, days):
        recent_date = timezone.now() - timedelta(days=days)
        return self.filter(order_date__gte=recent_date)
    
class RepairOrderQuerySet(models.QuerySet):
    def completed(self):
        return self.filter(status='completed')

    def unpaid(self):
        return self.filter(status='customer_pickup')

    def by_shop(self, shop_id):
        return self.filter(shop_id=shop_id)

    def sent_to_other_shop(self):
        return self.filter(status='sent_to_other_shop')

    def created_today(self):
        return self.filter(created_at__date=timezone.now().date())

    def paid(self):
        return self.filter(status='paid')

    def total_calculations(self):
        """Perform the daily calculations."""
        total_price = self.aggregate(total_price=models.Sum('total_price'))['total_price'] or 0
        total_expenses = self.aggregate(total_expenses=models.Sum('expenses'))['total_expenses'] or 0
        total_profit = total_price - total_expenses

        unpaid_orders = self.unpaid().count()
        sent_to_other_shop = self.sent_to_other_shop().count()

        # Profit division
        profit_owner = total_profit / 2
        profit_worker = total_profit / 2

        return {
            'total_price': total_price,
            'total_expenses': total_expenses,
            'total_profit': total_profit,
            'unpaid_orders': unpaid_orders,
            'sent_to_other_shop': sent_to_other_shop,
            'profit_owner': profit_owner,
            'profit_worker': profit_worker,
        }
