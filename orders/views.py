from django.shortcuts import render, get_object_or_404
from .models import RepairOrder


def repair_receipt_view(request, order_id):
    repair_order = get_object_or_404(RepairOrder, id=order_id)
    return render(request, 'orders/repair_receipt.html', {'repair_order': repair_order})

def blank_receipt_view(request):
    return render(request, 'orders/repair_receipt.html')

