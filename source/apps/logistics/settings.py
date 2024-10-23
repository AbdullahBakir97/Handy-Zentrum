LOGISTICS_SETTINGS = {
    "DEFAULT_SHIPPING_COMPANY": "DHL",
    "SHIPMENT_STATUSES": ["pending", "in_transit", "delivered", "returned"],
    "INTERACTION_TYPES": ["pickup", "delivered", "delay", "customs"],
}

LOGISTICS_TRACKING_URL_TEMPLATE = "https://tracking.company.com/{tracking_number}"
LOGISTICS_MAX_SHIPMENT_WEIGHT = 50
