from django.urls import path

from .views import (
    OrderCancelView,
    OrderCreateView,
    OrderDetailView,
    OrderFulfillmentView,
    OrderHistoryView,
    OrderReportView,
    PaymentProcessView,
    ShipmentTrackingView,
    blank_receipt_view,
    repair_receipt_view,
)

urlpatterns = [
    path(
        "repair-order/<int:order_id>/receipt/",
        repair_receipt_view,
        name="repair-receipt",
    ),
    path("repair-order/blank-receipt/", blank_receipt_view, name="blank-receipt"),
    path("orders/create/", OrderCreateView.as_view(), name="order_create"),
    path("orders/<int:order_id>/", OrderDetailView.as_view(), name="order_detail"),
    path(
        "orders/<int:order_id>/cancel/", OrderCancelView.as_view(), name="order_cancel"
    ),
    path(
        "orders/<int:order_id>/payment/",
        PaymentProcessView.as_view(),
        name="payment_process",
    ),
    path(
        "orders/history/<int:customer_id>/",
        OrderHistoryView.as_view(),
        name="order_history",
    ),
    path(
        "orders/<int:order_id>/shipment/tracking/",
        ShipmentTrackingView.as_view(),
        name="shipment_tracking",
    ),
    path(
        "orders/<int:order_id>/fulfill/",
        OrderFulfillmentView.as_view(),
        name="order_fulfill",
    ),
    path(
        "orders/<int:order_id>/report/", OrderReportView.as_view(), name="order_report"
    ),
]
