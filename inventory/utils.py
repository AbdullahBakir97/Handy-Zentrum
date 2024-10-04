from .models import Product, InventoryItem, StockAdjustment, InventoryTransfer, Warehouse
import random
import string



def calculate_stock_value(inventory_items):
    return sum(item.quantity * item.product.price for item in inventory_items)

def check_inventory_level(item):
    return item.quantity > 0


def add_stock(product, warehouse, quantity):
    inventory_item, created = InventoryItem.objects.get_or_create(product=product, location=warehouse, defaults={'quantity': 0})
    inventory_item.quantity += quantity
    inventory_item.save()

def remove_stock(product, warehouse, quantity):
    inventory_item = InventoryItem.objects.get(product=product, location=warehouse)
    if inventory_item.quantity >= quantity:
        inventory_item.quantity -= quantity
        inventory_item.save()

def transfer_stock(product, from_warehouse, to_warehouse, quantity):
    if InventoryItem.objects.filter(product=product, location=from_warehouse, quantity__gte=quantity).exists():
        # Remove stock from the source
        remove_stock(product, from_warehouse, quantity)
        # Add stock to the destination
        add_stock(product, to_warehouse, quantity)
        # Create a transfer record
        InventoryTransfer.objects.create(product=product, from_location=from_warehouse, to_location=to_warehouse, quantity=quantity, status='completed')

def bulk_import_products(product_data):
    # Assume product_data is a list of dictionaries
    products = []
    for data in product_data:
        product = Product(
            name=data['name'],
            description=data.get('description', ''),
            sku=data['sku'],
            category_id=data['category_id'],
            price=data['price']
        )
        product.save()
        products.append(product)
    return products

def export_products_to_csv(queryset):
    import csv
    from django.http import HttpResponse

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="products.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Name', 'SKU', 'Category', 'Price'])
    
    for product in queryset:
        writer.writerow([product.name, product.sku, product.category.name, product.price])

    return response