import random
import requests
import string
from datetime import timedelta
from django.core.cache import cache


def generate_tracking_number():
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=10))


def calculate_estimated_arrival(shipped_date, distance):
    if distance < 500:
        return shipped_date + timedelta(days=1)
    elif distance < 2000:
        return shipped_date + timedelta(days=3)
    else:
        return shipped_date + timedelta(days=7)


# def calculate_estimated_arrival(shipped_date, transit_days=5):
#     return shipped_date + timedelta(days=transit_days)


def get_shipment_status(tracking_number):
    # Simulate third-party API interaction
    response = requests.get(f"https://api.dhl.com/track/{tracking_number}")
    return response.json().get("status", "unknown")


def adjust_stock_level(inventory_item, quantity, adjustment_type):
    if adjustment_type == "add":
        inventory_item.quantity += quantity
    elif adjustment_type == "remove":
        inventory_item.quantity -= quantity
    inventory_item.save()


def get_cached_shipment_status(tracking_number):
    status = cache.get(f"shipment_status_{tracking_number}")
    if not status:
        status = get_shipment_status(tracking_number)
        cache.set(
            f"shipment_status_{tracking_number}", status, timeout=3600
        )  # Cache for 1 hour
    return status
