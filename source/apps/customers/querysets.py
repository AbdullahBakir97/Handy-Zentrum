from django.db import models
from django.db.models import Count


class CustomerQuerySet(models.QuerySet):
    def loyalty_members(self):
        return self.filter(is_loyalty_member=True)

    def with_loyalty_points_above(self, points):
        return self.filter(loyalty_points__gt=points)

    def by_loyalty_tier(self, tier):
        return self.filter(loyalty_program__tier=tier)

    def active_customers(self):
        return self.filter(is_loyalty_member=True)

    def inactive_customers(self):
        return self.filter(loyalty_points=0, customer_interactions__isnull=True)

    def with_interactions(self):
        return self.annotate(interactions_count=Count("customer_interactions")).filter(
            interactions_count__gt=0
        )

    def without_interactions(self):
        return self.annotate(interactions_count=Count("customer_interactions")).filter(
            interactions_count=0
        )

    def top_customers_by_loyalty_points(self):
        return self.filter(is_loyalty_member=True).order_by("-loyalty_program__points")

    def by_join_date_range(self, start_date, end_date):
        return self.filter(date_joined__range=(start_date, end_date))


class CustomerInteractionQuerySet(models.QuerySet):
    def inquiries(self):
        return self.filter(interaction_type="inquiry")

    def complaints(self):
        return self.filter(interaction_type="complaint")

    def within_last_month(self):
        from django.utils import timezone
        from datetime import timedelta

        one_month_ago = timezone.now() - timedelta(days=30)
        return self.filter(interaction_date__gte=one_month_ago)
