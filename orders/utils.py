import uuid
from decimal import Decimal
from django.core.exceptions import ValidationError
from django.core.mail import send_mail


def calculate_order_total(order):
    total = sum(item.total_price for item in order.items.all())
    return total

def generate_invoice(order):
    # Placeholder logic for generating a PDF invoice
    return f"Invoice for Order {order.id}"

def notify_customer(order, message):
    # Logic to send notifications (e.g., via email or SMS)
    print(f"Notify {order.customer.name}: {message}")
    


def generate_order_number():
    """Generates a unique order number."""
    return str(uuid.uuid4())

def calculate_order_total(order_items):
    """Calculates the total cost of the order, including taxes and discounts."""
    total = Decimal('0.00')
    for item in order_items:
        total += item.total_price
    # Add taxes, discounts, or any other applicable fees
    # Example: total += apply_tax(total)
    return total

def validate_order_data(order_data):
    """Validates order data such as customer information and shipping address."""
    required_fields = ['customer', 'shipping_address']
    for field in required_fields:
        if field not in order_data or not order_data[field]:
            raise ValidationError(f"{field} is required.")

def is_order_cancelable(order_status):
    """Returns True if the order is in a cancelable state."""
    cancelable_statuses = ['pending', 'processed']
    return order_status in cancelable_statuses

def get_order_status(order_id):
    """Retrieves the current status of the given order."""
    from orders.models import Order
    try:
        order = Order.objects.get(id=order_id)
        return order.status
    except Order.DoesNotExist:
        raise ValueError(f"Order {order_id} does not exist.")
    
# payment utils 

def validate_payment_details(payment_data):
    """Validates the provided payment details."""
    if 'payment_method' not in payment_data or not payment_data['payment_method']:
        raise ValidationError("Payment method is required.")
    # Add further validation depending on the payment method
    # Example: Validate credit card details if the method is credit card

def calculate_payment_fee(payment_method, amount):
    """Calculates any additional fees for a specific payment method."""
    fees = {
        'credit_card': Decimal('0.03'),  # 3% fee for credit cards
        'paypal': Decimal('0.02'),  # 2% fee for PayPal
        'cash_on_delivery': Decimal('0.00')  # No fee for cash
    }
    fee_percentage = fees.get(payment_method, Decimal('0.00'))
    return amount * fee_percentage

def apply_payment_discount(order, discount_code):
    """Applies a discount based on the given discount code."""
    # Example: Apply a fixed or percentage discount to the order's total
    if discount_code == 'PROMO10':
        discount = order.total_amount * Decimal('0.10')  # 10% discount
        order.total_amount -= discount
        order.save()

def generate_payment_reference(order_id):
    """Generates a unique payment reference number."""
    return f'PAY-{uuid.uuid4()}'

# Shipping Utils

def get_shipping_options(destination):
    """Fetches available shipping options for the provided destination."""
    # Example: Query available shipping options based on the destination
    shipping_options = ['Standard', 'Express', 'Next-Day']
    return shipping_options

def calculate_shipping_cost(order_items, destination):
    """Calculates the shipping cost based on the destination and items."""
    weight = sum(item.product.weight for item in order_items)
    # Calculate cost based on weight and destination
    if destination == 'international':
        return Decimal('50.00')  # Example fixed cost for international shipping
    return Decimal('10.00')  # Example domestic shipping cost

def validate_shipping_address(address_data):
    """Validates the shipping address to ensure it's deliverable."""
    if not address_data.get('city') or not address_data.get('postal_code'):
        raise ValidationError("Incomplete shipping address.")
    # You can also integrate with external services for address validation
    
# Order Fulfillment Utils

def check_inventory_availability(order_items):
    """Checks if there is enough stock for each item in the order."""
    for item in order_items:
        if item.product.stock < item.quantity:
            raise ValidationError(f"Product {item.product.name} is out of stock.")

def allocate_inventory(order_items):
    """Reserves inventory for the order items."""
    for item in order_items:
        item.product.stock -= item.quantity
        item.product.save()

def update_inventory_after_order(order_id):
    """Updates inventory after the order is processed."""
    from orders.models import Order
    order = Order.objects.get(id=order_id)
    for item in order.items.all():
        item.product.stock -= item.quantity
        item.product.save()
        
# Notifications and Alerts Utils

def send_order_confirmation(order):
    """Sends an email confirmation after the order is placed."""
    subject = f"Order Confirmation - {order.id}"
    message = f"Thank you for your order! Your order ID is {order.id}."
    send_mail(subject, message, 'no-reply@shop.com', [order.customer.email])

def send_payment_confirmation(order):
    """Sends a payment confirmation to the customer."""
    subject = f"Payment Confirmation - Order {order.id}"
    message = f"Your payment for Order {order.id} has been received."
    send_mail(subject, message, 'no-reply@shop.com', [order.customer.email])

def send_order_shipment_notification(order):
    """Sends a notification when the order has been shipped."""
    subject = f"Order Shipped - {order.id}"
    message = f"Your order has been shipped! Tracking Number: {order.tracking_number}"
    send_mail(subject, message, 'no-reply@shop.com', [order.customer.email])

def send_order_cancellation_alert(order):
    """Sends a cancellation alert to the customer."""
    subject = f"Order Canceled - {order.id}"
    message = f"Your order {order.id} has been canceled. A refund will be processed."
    send_mail(subject, message, 'no-reply@shop.com', [order.customer.email])
    
# Miscellaneous Utils

def generate_order_report(order):
    """Generates a detailed report for an order."""
    report = f"Order Report for Order {order.id}\n"
    report += f"Customer: {order.customer.user}\n"
    report += f"Total Amount: {order.total_amount}\n"
    for item in order.items.all():
        report += f"{item.product.name}: {item.quantity} x {item.price_per_item} = {item.total_price}\n"
    return report

def format_order_summary(order):
    """Formats order data into a summary."""
    summary = {
        "order_id": order.id,
        "customer": order.customer.user,
        "items": [{
            "product": item.product.name,
            "quantity": item.quantity,
            "total_price": item.total_price,
        } for item in order.items.all()],
        "total_amount": order.total_amount,
        "status": order.status
    }
    return summary