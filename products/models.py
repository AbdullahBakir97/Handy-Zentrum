from django.db import models
from django.forms import ValidationError
from django.utils.text import slugify
from taggit.managers import TaggableManager
from django.utils.translation import gettext_lazy as _



class Brand(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    slug = models.SlugField(unique=True, max_length=255, blank=True, null=True)
    image = models.ImageField(upload_to='brand_images/', blank=True, null=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Brand'
        verbose_name_plural = 'Brands'

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
class Category(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    slug = models.SlugField(unique=True, max_length=255, blank=True, null=True)
    parent = models.ForeignKey('self', blank=True, null=True, on_delete=models.SET_NULL, related_name='child_categories')
    image = models.ImageField(upload_to='category_images/', blank=True, null=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

    def __str__(self):
        return f'{self.name}' if not self.parent else f'{self.name} (Subcategory of {self.parent.name})'

    def clean(self):
        """Ensure a category cannot be its own parent."""
        if self.parent == self:
            raise ValidationError("A category cannot be its own parent.")
        
    def delete(self):
        self.is_active = False
        self.save()
        
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    
class Product(models.Model):
    FLAG_TYPES =(
    ('Sale','Sale'),
    ('New','New'),
    ('Feature','Feature'),
    )
    name = models.CharField(max_length=150)
    subtitle = models.TextField(max_length=500)
    description = models.TextField(blank=True, null=True, max_length=100000)
    category = models.ForeignKey(Category, 
            on_delete=models.CASCADE, 
            related_name='products_in_category'
    )
    brand = models.ForeignKey(Brand, 
        on_delete=models.SET_NULL,
        null=True, blank=True, 
        related_name='products_brands'
    )
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    flag = models.CharField(_('Flag'),max_length=10,choices=FLAG_TYPES)
    slug = models.SlugField(unique=True, max_length=255, blank=True, null=True)
    sku = models.CharField(max_length=15, unique=True, blank=True, null=True)
    tags = TaggableManager()
    image = models.ImageField(upload_to='product_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Product'
        verbose_name_plural = 'Products'

    def __str__(self):
        return f'{self.name}'

    def total_stock(self):
        """Calculate total stock available for this product."""
        return self.inventory_records.aggregate(total=models.Sum('quantity'))['total'] or 0
    
    def available_in_warehouses(self):
        # Check stock availability across all warehouses
        available_warehouses = self.inventory_records.filter(quantity__gt=0)
        return available_warehouses

    def apply_discount(self, percentage):
        """Apply a discount to the base price."""
        discount_amount = self.base_price * (percentage / 100)
        return self.base_price - discount_amount
    
    def delete(self):
        self.is_active = False
        self.save()
        
    def save(self, *args, **kwargs):
        regenerate_sku = False

        # If the product already exists in the database
        if self.pk and Product.objects.filter(pk=self.pk).exists():
            old_product = Product.objects.get(pk=self.pk)

            # Check if the name has changed
            if old_product.name != self.name:
                self.slug = slugify(self.name)
                from .utils import BaseSKUGenerator
                sku_generator = BaseSKUGenerator()
                self.sku = sku_generator.generate_sku(self)
                regenerate_sku = True  # Flag that SKU has been regenerated

        else:
            # First-time creation, generate slug and SKU if not set
            if not self.slug:
                self.slug = slugify(self.name)
            if not self.sku:
                from .utils import BaseSKUGenerator
                sku_generator = BaseSKUGenerator()
                self.sku = sku_generator.generate_sku(self)

        super().save(*args, **kwargs)

        # Update variant SKUs if product SKU changes or for the first time
        self.update_variant_skus()

    def update_variant_skus(self):
        """
        Check and update all variant SKUs to ensure they match the base product SKU.
        If a variant SKU doesn't follow the 'PRODUCTSKU-R-M' format, it gets updated.
        """
        for variant in self.variants.all():
            expected_variant_sku = f"{self.sku}-{variant.color[:1].upper()}-{variant.size[:1].upper()}"

            if variant.sku != expected_variant_sku:
                # Update the variant SKU to match the format
                variant.sku = expected_variant_sku
                variant.save()

class ProductImages(models.Model):
    product = models.ForeignKey(Product,related_name='product_images',on_delete=models.CASCADE)
    image = models.ImageField(upload_to='product_images/')

    def __str__(self):
        return str(self.product)
    
class ProductVariant(models.Model):
    product = models.ForeignKey(Product, related_name='variants', on_delete=models.CASCADE)
    color = models.CharField(max_length=50, blank=True, null=True)
    size = models.CharField(max_length=50, blank=True, null=True)
    sku = models.CharField(max_length=20, unique=True, blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    weight = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    dimensions = models.CharField(max_length=100, blank=True, null=True)
    stock = models.PositiveIntegerField(default=0)
    variant_group = models.CharField(max_length=50, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['product', 'color', 'size']

    def __str__(self):
        return f"{self.product.name} - {self.color} - {self.size}"

    def reserve_stock(self, quantity):
        """Reserve stock for an order."""
        if self.stock >= quantity:
            self.stock -= quantity
            self.save()
            return True
        return False

    def delete(self):
        self.is_active = False
        self.save()
        
    def save(self, *args, **kwargs):
        # Validate uniqueness of the color and size combination for the product
        from .utils import ProductValidation
        variant_data = {
            'color': self.color,
            'size': self.size,
        }
        ProductValidation.validate_variant_uniqueness(self.product, variant_data)

        # Generate SKU based on product SKU, color, and size
        expected_sku = f"{self.product.sku}-{self.color[:1].upper()}-{self.size[:1].upper()}"

        # Set SKU if not already set or if there's a mismatch
        if not self.sku or self.sku != expected_sku:
            self.sku = expected_sku

        # Call the parent save method to persist the changes
        super().save(*args, **kwargs)




