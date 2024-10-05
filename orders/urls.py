from django.urls import path
from .views import repair_receipt_view, blank_receipt_view

urlpatterns = [
    path('repair-order/<int:order_id>/receipt/', repair_receipt_view, name='repair-receipt'),
    path('repair-order/blank-receipt/', blank_receipt_view, name='blank-receipt'),
]
