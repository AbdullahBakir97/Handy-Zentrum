from .services import (
    OrderService, PaymentService, ShippingService, FulfillmentService, 
    NotificationService, ReportingService, CachingService, RepairCalculationService
)

class OrderController:
    def __init__(self):
        self.order_service = OrderService()
        self.fulfillment_service = FulfillmentService()
        self.notification_service = NotificationService()
        self.caching_service = CachingService()

    def create_order(self, customer_id, order_data):
        order = self.order_service.create_order(customer_id, order_data)
        self.notification_service.send_order_notifications(order)
        self.caching_service.cache_order_data(order)
        return order

    def get_order_details(self, order_id):
        cached_order = self.caching_service.get_cached_order_data(order_id)
        if cached_order:
            return cached_order
        order = self.order_service.get_order_details(order_id)
        self.caching_service.cache_order_data(order)
        return order

    def cancel_order(self, order_id):
        self.order_service.cancel_order(order_id)
        self.caching_service.invalidate_cache(order_id)
        return {'status': 'Order canceled successfully'}

    def apply_order_discount(self, order_id, discount_code):
        self.order_service.apply_order_discount(order_id, discount_code)
        self.caching_service.invalidate_cache(order_id)

    def process_order_fulfillment(self, order_id):
        self.fulfillment_service.process_order_fulfillment(order_id)
        return {'status': 'Order fulfillment processed'}

    def get_order_history(self, customer_id):
        return self.order_service.get_order_history(customer_id)


class PaymentController:
    def __init__(self):
        self.payment_service = PaymentService()

    def process_payment(self, order_id, payment_method):
        self.payment_service.process_payment(order_id, payment_method)
        return {'status': 'Payment processed successfully'}

    def refund_payment(self, order_id):
        self.payment_service.refund_payment(order_id)
        return {'status': 'Payment refunded successfully'}


class ShippingController:
    def __init__(self):
        self.shipping_service = ShippingService()

    def create_shipment(self, order_id, shipping_address, shipping_method):
        shipment = self.shipping_service.create_shipment(order_id, shipping_address, shipping_method)
        return shipment

    def track_shipment(self, order_id):
        tracking_info = self.shipping_service.track_shipment(order_id)
        return tracking_info

    def cancel_shipment(self, shipment_id):
        self.shipping_service.cancel_shipment(shipment_id)
        return {'status': 'Shipment canceled successfully'}


class ReportingController:
    def __init__(self):
        self.reporting_service = ReportingService()

    def generate_order_report(self, order_id):
        return self.reporting_service.generate_order_report(order_id)

    def generate_sales_report(self, start_date, end_date):
        return self.reporting_service.generate_sales_report(start_date, end_date)


class RepairController:
    def __init__(self):
        self.repair_service = RepairCalculationService()

    def calculate_daily_totals(self, shop=None):
        return self.repair_service.calculate_daily_totals(shop)

    def verify_calculations(self):
        return self.repair_service.verify_calculations()