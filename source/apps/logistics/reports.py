from django.db import models
from .models import Shipment, LogisticsInteraction, ReturnShipment
from django.db.models import Count, Sum, Q


class LogisticsReports:
    def delayed_shipments_report(self, start_date, end_date):
        return Shipment.objects.delayed_shipments().filter(
            created_at__range=(start_date, end_date)
        )

    def customs_delay_report(self):
        return LogisticsInteraction.objects.interactions_by_type("customs")

    @staticmethod
    def get_shipments_summary():
        return Shipment.objects.values("status").annotate(count=Count("status"))

    @staticmethod
    def get_shipment_count_by_status(status):
        return Shipment.objects.filter(status=status).count()

    @staticmethod
    def get_recent_deliveries():
        return Shipment.objects.filter(status="delivered").order_by("-delivered_date")[
            :10
        ]


class ReturnReports:
    def returns_summary(self, start_date, end_date):
        return ReturnShipment.objects.filter(created_at__range=(start_date, end_date))

    def returns_by_status(self, status):
        return ReturnShipment.objects.filter(status=status)

    @staticmethod
    def get_return_summary():
        return ReturnShipment.objects.values("status").annotate(count=Count("status"))

    @staticmethod
    def get_recent_returns():
        return ReturnShipment.objects.filter(status="received").order_by(
            "-received_at"
        )[:10]


class ShipmentReports:
    def average_delivery_time(self):
        delivered_shipments = Shipment.objects.filter(status="delivered")
        return delivered_shipments.aggregate(
            average_time=models.Avg(
                models.F("estimated_arrival") - models.F("shipped_date")
            )
        )
