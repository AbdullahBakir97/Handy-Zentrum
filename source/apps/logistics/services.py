from .models import Shipment, ReturnShipment
from datetime import timedelta
from django.utils import timezone
from .utils import generate_tracking_number, calculate_estimated_arrival
import requests
from django.conf import settings
from django.core.cache import cache


class ShipmentService:
    def create_shipment(self, product, quantity, origin, destination):
        shipment = Shipment.objects.create(
            product=product,
            quantity=quantity,
            origin=origin,
            destination=destination,
            shipped_date=timezone.now(),
            estimated_arrival=calculate_estimated_arrival(origin, destination),
            tracking_number=generate_tracking_number(),
            status="pending",
        )
        return shipment

    def update_shipment_status(self, shipment, status):
        shipment.status = status
        shipment.save()


class ReturnService:
    def initiate_return(self, shipment, reason):
        return_shipment = ReturnShipment.objects.create(
            shipment=shipment, reason=reason, status="initiated"
        )
        return return_shipment


class ShipmentTrackingService:

    @staticmethod
    def get_tracking_info(tracking_number):
        url = settings.LOGISTICS_TRACKING_URL_TEMPLATE.format(
            tracking_number=tracking_number
        )
        response = requests.get(url)
        return response.json()  # Assuming the API returns JSON


class ShipmentCacheService:

    @staticmethod
    def get_tracking_info_cached(tracking_number):
        cache_key = f"tracking_info_{tracking_number}"
        tracking_info = cache.get(cache_key)

        if not tracking_info:
            tracking_info = ShipmentTrackingService.get_tracking_info(tracking_number)
            cache.set(cache_key, tracking_info, 3600)  # Cache for 1 hour

        return tracking_info
