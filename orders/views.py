from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from .controllers import (
    OrderController, PaymentController, ShippingController, 
    FulfillmentController, ReportingController
)
from .models import Order, RepairOrder
from django.contrib import messages


def repair_receipt_view(request, order_id):
    repair_order = get_object_or_404(RepairOrder, id=order_id)
    return render(request, 'orders/repair_receipt.html', {'repair_order': repair_order})

def blank_receipt_view(request):
    return render(request, 'orders/repair_receipt.html')


# View to create an order
class OrderCreateView(View):
    template_name = 'orders/order_create.html'

    def get(self, request, *args, **kwargs):
        # You could load necessary data for creating an order like products or customer information.
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        customer_id = request.POST.get('customer_id')
        order_data = request.POST.dict()  # Extract all order data from form
        try:
            order = OrderController().create_order(customer_id, order_data)
            messages.success(request, "Order successfully created!")
            return redirect('order_detail', order_id=order.id)
        except Exception as e:
            messages.error(request, str(e))
            return render(request, self.template_name)

# View to display order details
class OrderDetailView(View):
    template_name = 'orders/order_detail.html'

    def get(self, request, order_id, *args, **kwargs):
        order = get_object_or_404(Order, id=order_id)
        order_details = OrderController().get_order_details(order_id)
        return render(request, self.template_name, {'order': order_details})

# View to cancel an order
class OrderCancelView(View):
    def post(self, request, order_id, *args, **kwargs):
        try:
            OrderController().cancel_order(order_id)
            messages.success(request, "Order canceled successfully!")
        except Exception as e:
            messages.error(request, str(e))
        return redirect('order_list')

# View for processing a payment
class PaymentProcessView(View):
    template_name = 'orders/payment_process.html'

    def get(self, request, order_id, *args, **kwargs):
        order = get_object_or_404(Order, id=order_id)
        return render(request, self.template_name, {'order': order})

    def post(self, request, order_id, *args, **kwargs):
        payment_method = request.POST.get('payment_method')
        try:
            PaymentController().process_payment(order_id, payment_method)
            messages.success(request, "Payment processed successfully!")
            return redirect('order_detail', order_id=order_id)
        except Exception as e:
            messages.error(request, str(e))
            return redirect('payment_process', order_id=order_id)

# View to display order history of a customer
class OrderHistoryView(View):
    template_name = 'orders/order_history.html'

    def get(self, request, customer_id, *args, **kwargs):
        order_history = OrderController().get_order_history(customer_id)
        return render(request, self.template_name, {'order_history': order_history})

# View to track shipment status
class ShipmentTrackingView(View):
    template_name = 'orders/shipment_tracking.html'

    def get(self, request, order_id, *args, **kwargs):
        try:
            shipment_status = ShippingController().track_shipment(order_id)
            return render(request, self.template_name, {'shipment_status': shipment_status})
        except Exception as e:
            messages.error(request, str(e))
            return redirect('order_detail', order_id=order_id)

# View for order fulfillment
class OrderFulfillmentView(View):
    def post(self, request, order_id, *args, **kwargs):
        try:
            FulfillmentController().process_fulfillment(order_id)
            messages.success(request, "Order fulfilled successfully!")
        except Exception as e:
            messages.error(request, str(e))
        return redirect('order_detail', order_id=order_id)

# View for generating an order report
class OrderReportView(View):
    template_name = 'orders/order_report.html'

    def get(self, request, order_id, *args, **kwargs):
        order_report = ReportingController().generate_order_report(order_id)
        return render(request, self.template_name, {'order_report': order_report})