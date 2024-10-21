# import logging
#
# from django.db.models.signals import post_save
# from django.dispatch import receiver
#
# from .models import Product, ProductVariant
# from .services import ProductService
# from .utils import BaseSKUGenerator, ProductValidation, VariantSKUGenerator

# logger = logging.getLogger(__name__)

# # Initialize the services (you might want to do this in a more centralized way)
# base_sku_generator = BaseSKUGenerator()
# variant_sku_generator = VariantSKUGenerator()
# validation = ProductValidation()
# product_service = ProductService(base_sku_generator, variant_sku_generator, validation)


# @receiver(post_save, sender=Product)
# def create_product_variants(sender, instance, created, **kwargs):
#     if created and not instance.sku:
#         # Temporarily disconnect the signal to avoid recursion
#         post_save.disconnect(create_product_variants, sender=Product)

#         try:
#             # Generate SKU using the service (if needed)
#             instance.sku = base_sku_generator.generate_sku(instance)

#             # Save the instance after SKU generation
#             instance.save(update_fields=['sku'])

#             # Create the product and its variants using the ProductService
#             product_service.create_product(product_data={
#                 'name': instance.name,
#                 'category': instance.category,
#                 'description': instance.description,
#                 'base_price': instance.base_price,
#                 # Add other product fields as needed
#             }, variant_data_list=[
#                 # Add variant data here
#             ])
#         finally:
#             # Reconnect the signal
#             post_save.connect(create_product_variants, sender=Product)
