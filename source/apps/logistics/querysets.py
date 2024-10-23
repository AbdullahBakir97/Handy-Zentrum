from django.db import models
from django.utils import timezone


class ShipmentQuerySet(models.QuerySet):
    def pending_shipments(self):
        return self.filter(status="pending")

    def in_transit(self):
        return self.filter(status="in_transit")

    def delivered(self):
        return self.filter(status="delivered")

    def delivered_in_last_week(self):
        last_week = timezone.now() - timezone.timedelta(days=7)
        return self.filter(status="delivered", delivered_date__gte=last_week)

    def delayed_shipments(self):
        return self.filter(logistics_interactions__interaction_type="delay")

    def shipments_by_company(self, company_name):
        return self.filter(shipping_company=company_name)

    def shipments_by_destination(self, destination):
        return self.filter(destination__icontains=destination)

    def shipments_between_dates(self, start_date, end_date):
        return self.filter(created_at__range=(start_date, end_date))


class LogisticsInteractionQuerySet(models.QuerySet):
    def interactions_by_type(self, interaction_type):
        return self.filter(interaction_type=interaction_type)

    def recent_interactions(self):
        return self.order_by("-timestamp")[:10]

    def by_shipment(self, shipment_id):
        return self.filter(shipment_id=shipment_id)

    def delays(self):
        return self.filter(interaction_type="delay")


class ReturnShipmentQuerySet(models.QuerySet):
    def returns_in_transit(self):
        return self.filter(status="in_transit")

    def returns_received(self):
        return self.filter(status="received")

    def returns_by_reason(self, reason):
        return self.filter(reason__icontains=reason)
