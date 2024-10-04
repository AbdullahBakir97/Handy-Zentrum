import random
import string
from .models import Product

def generate_sku():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

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

