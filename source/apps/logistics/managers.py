from django.db import models
from .querysets import (
    ShipmentQuerySet,
    LogisticsInteractionQuerySet,
    ReturnShipmentQuerySet,
)


class ShipmentManager(models.Manager):
    def get_queryset(self):
        return ShipmentQuerySet(self.model, using=self._db)

    def pending_shipments(self):
        return self.get_queryset().pending_shipments()

    def in_transit(self):
        return self.get_queryset().in_transit()

    def delivered(self):
        return self.get_queryset().delivered()

    def delivered_in_last_week(self):
        return self.get_queryset().delivered_in_last_week()

    def delayed_shipments(self):
        return self.get_queryset().delayed_shipments()

    def shipments_by_company(self, company_name):
        return self.get_queryset().shipments_by_company(company_name)

    def shipments_by_destination(self, destination):
        return self.get_queryset().shipments_by_destination(destination)

    def shipments_between_dates(self, start_date, end_date):
        return self.get_queryset().shipments_between_dates(start_date, end_date)


class LogisticsInteractionManager(models.Manager):
    def get_queryset(self):
        return LogisticsInteractionQuerySet(self.model, using=self._db)

    def interactions_by_type(self, interaction_type):
        return self.get_queryset().interactions_by_type(interaction_type)

    def recent_interactions(self):
        return self.get_queryset().recent_interactions()

    def by_shipment(self, shipment_id):
        return self.get_queryset().by_shipment(shipment_id)

    def delays(self):
        return self.get_queryset().delays()


class ReturnShipmentManager(models.Manager):
    def get_queryset(self):
        return ReturnShipmentQuerySet(self.model, using=self._db)

    def returns_in_transit(self):
        return self.get_queryset().returns_in_transit()

    def returns_received(self):
        return self.get_queryset().returns_received()

    def returns_by_reason(self, reason):
        return self.get_queryset().returns_by_reason(reason)
