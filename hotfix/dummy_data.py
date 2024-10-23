import os

import django

from source.apps.logistics.models import LogisticsInteraction, ReturnShipment, Shipment
from source.apps.products.models import Category

# Set the DJANGO_SETTINGS_MODULE to point to your project's settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")
# Initialize Django
django.setup()

import random

from django.contrib.auth.models import User
from faker import Faker

from source.apps.customers.models import Customer, CustomerInteraction, LoyaltyProgram
from source.apps.inventory.models import (
    InventoryItem,
    InventoryTransfer,
    Product,
    StockAdjustment,
    Warehouse,
)
from source.apps.orders.models import Order, OrderItem, Payment
from source.apps.sales_analytics.models import (
    SalesByCustomerSegment,
    SalesByProduct,
    SalesReport,
)

faker = Faker()


# Create Users
def create_users(n):
    users = []
    for _ in range(n):
        user = User.objects.create_user(
            username=faker.user_name(),
            email=faker.email(),
            password=faker.password(),
        )
        users.append(user)
    return users


# Create Customers
def create_customers(users):
    customers = []
    for user in users:
        customer = Customer.objects.create(
            user=user,
            first_name=faker.first_name(),
            last_name=faker.last_name(),
            email=user.email,
            phone_number=faker.phone_number(),
            address=faker.address(),
            city=faker.city(),
            country=faker.country(),
            is_loyalty_member=random.choice([True, False]),
            loyalty_points=random.randint(0, 1000),
        )
        customers.append(customer)
    return customers


# Create Categories
def create_categories(n=5):
    categories = []
    for _ in range(n):
        category = Category.objects.create(
            name=faker.word(),
            description=faker.sentence(),
        )
        categories.append(category)
    return categories


# Create Products
def create_products(categories, n=20):
    products = []
    for _ in range(n):
        try:
            product = Product.objects.create(
                name=faker.word(),
                description=faker.text(),
                sku=faker.unique.ean(length=13),
                category=random.choice(categories),
                price=random.uniform(10.00, 1000.00),
            )
            products.append(product)
        except Exception as e:
            print(f"Error creating product: {e}")
    return products


# Create Warehouses
def create_warehouses(users, n=5):
    warehouses = []
    for _ in range(n):
        warehouse = Warehouse.objects.create(
            name=faker.company(), location=faker.address(), manager=random.choice(users)
        )
        warehouses.append(warehouse)
    return warehouses


# Create InventoryItems
def create_inventory_items(products, warehouses, n=50):
    for _ in range(n):
        InventoryItem.objects.create(
            product=random.choice(products),
            quantity=random.randint(10, 200),
            location=random.choice(warehouses),
            status=random.choice(["in_stock", "reserved", "sold"]),
        )


# Create Stock Adjustments
def create_stock_adjustments(inventory_items, users, n=30):
    for _ in range(n):
        StockAdjustment.objects.create(
            inventory_item=random.choice(inventory_items),
            adjustment_type=random.choice(["add", "remove"]),
            quantity=random.randint(1, 50),
            reason=faker.sentence(),
            performed_by=random.choice(users),
        )


# Create Inventory Transfers
def create_inventory_transfers(products, warehouses, users, n=15):
    for _ in range(n):
        InventoryTransfer.objects.create(
            product=random.choice(products),
            from_location=random.choice(warehouses),
            to_location=random.choice(warehouses),
            quantity=random.randint(1, 50),
            initiated_by=random.choice(users),
            status=random.choice(["pending", "completed"]),
        )


# Create Customer Interactions
def create_customer_interactions(customers, n=30):
    for _ in range(n):
        CustomerInteraction.objects.create(
            customer=random.choice(customers),
            interaction_type=random.choice(["inquiry", "complaint", "feedback"]),
            notes=faker.text(),
        )


# Create Loyalty Programs
def create_loyalty_programs(customers):
    for customer in customers:
        if customer.is_loyalty_member:
            LoyaltyProgram.objects.create(
                customer=customer,
                points=random.randint(100, 500),
                tier=random.choice(["bronze", "silver", "gold"]),
            )


# Create Orders and Order Items
def create_orders(customers, products, n=50):
    orders = []
    for _ in range(n):
        order = Order.objects.create(
            customer=random.choice(customers),
            status=random.choice(
                ["pending", "processed", "shipped", "delivered", "canceled"]
            ),
            total_amount=random.uniform(50.00, 5000.00),
            shipping_address=faker.address(),
            payment_status=random.choice(["paid", "unpaid", "refunded"]),
        )
        orders.append(order)
        for _ in range(random.randint(1, 5)):
            OrderItem.objects.create(
                order=order,
                product=random.choice(products),
                quantity=random.randint(1, 10),
                price_per_item=random.uniform(10.00, 500.00),
                total_price=random.uniform(10.00, 500.00) * random.randint(1, 10),
            )
    return orders


# Create Payments
def create_payments(orders):
    for order in orders:
        Payment.objects.create(
            order=order,
            payment_method=random.choice(["credit_card", "paypal", "cash_on_delivery"]),
            payment_status=random.choice(["paid", "pending", "failed"]),
        )


# Create Shipments
def create_shipments(products, warehouses, n=30):
    shipments = []
    for _ in range(n):
        shipment = Shipment.objects.create(
            product=random.choice(products),
            quantity=random.randint(1, 50),
            origin=random.choice(warehouses),
            destination=faker.address(),
            shipped_date=faker.date_time_this_year(),
            estimated_arrival=faker.date_time_this_year(),
            tracking_number=faker.unique.bothify(text="??-########"),
            shipping_company="DHL",
            status=random.choice(["pending", "in_transit", "delivered", "returned"]),
        )
        shipments.append(shipment)
    return shipments


# Create Logistics Interactions
def create_logistics_interactions(shipments, n=20):
    for shipment in shipments:
        LogisticsInteraction.objects.create(
            shipment=shipment,
            interaction_type=random.choice(["pickup", "delivered", "delay", "customs"]),
            notes=faker.text(),
        )


# Create Return Shipments
def create_return_shipments(shipments):
    for shipment in shipments:
        if shipment.status == "returned":
            ReturnShipment.objects.create(
                shipment=shipment,
                reason=faker.sentence(),
                received_at=faker.date_time_this_year(),
                status=random.choice(
                    ["initiated", "in_transit", "received", "refunded"]
                ),
            )


# Create Sales Reports and related models
def create_sales_reports(products, n=10):
    for _ in range(n):
        report = SalesReport.objects.create(
            total_sales=random.uniform(500.00, 10000.00),
            total_orders=random.randint(50, 200),
            total_customers=random.randint(20, 100),
            average_order_value=random.uniform(20.00, 500.00),
            highest_selling_product=random.choice(products),
        )
        for product in products:
            SalesByProduct.objects.create(
                product=product,
                total_units_sold=random.randint(10, 100),
                total_revenue=random.uniform(500.00, 5000.00),
                report=report,
            )
        SalesByCustomerSegment.objects.create(
            segment=random.choice(["Retail", "Wholesale", "Online"]),
            total_sales=random.uniform(500.00, 5000.00),
            total_orders=random.randint(10, 100),
            report=report,
        )


# Execute the data creation
if __name__ == "__main__":
    users = create_users(10)
    categories = create_categories()
    products = create_products(categories)
    warehouses = create_warehouses(users)
    create_inventory_items(products, warehouses)
    inventory_items = InventoryItem.objects.all()
    create_stock_adjustments(inventory_items, users)
    create_inventory_transfers(products, warehouses, users)
    customers = create_customers(users)
    create_customer_interactions(customers)
    create_loyalty_programs(customers)
    orders = create_orders(customers, products)
    create_payments(orders)
    shipments = create_shipments(products, warehouses)
    create_logistics_interactions(shipments)
    create_return_shipments(shipments)
    create_sales_reports(products)
