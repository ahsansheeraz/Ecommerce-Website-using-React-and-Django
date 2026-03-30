"""
Product models for e-commerce platform.
Handles categories, brands, products, inventory, reviews and related functionality.
"""

from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.text import slugify
from users.models import User
import uuid

class Category(models.Model):
    """
    Product category model for hierarchical categorization.
    Supports parent-child relationship for subcategories.
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    description = models.TextField(max_length=500, blank=True)
    
    # Parent category for subcategories
    parent = models.ForeignKey(
        'self', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True, 
        related_name='children'
    )
    
    # Category image and icons
    image = models.ImageField(upload_to='categories/', null=True, blank=True)
    icon = models.CharField(max_length=50, blank=True, help_text="FontAwesome icon class")
    
    # Metadata
    is_active = models.BooleanField(default=True)
    featured = models.BooleanField(default=False, help_text="Show on homepage")
    meta_title = models.CharField(max_length=100, blank=True)
    meta_description = models.CharField(max_length=200, blank=True)
    
    # SEO fields
    meta_keywords = models.CharField(max_length=255, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        ordering = ['name']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['is_active', 'featured']),
        ]
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        """
        Auto-generate slug from name if not provided.
        """
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def get_full_path(self):
        """
        Get full category path (e.g., Electronics > Mobile Phones > Smartphones)
        """
        if self.parent:
            return f"{self.parent.get_full_path()} > {self.name}"
        return self.name
    
    @property
    def product_count(self):
        """Get count of active products in this category."""
        return self.products.filter(is_active=True).count()


class Brand(models.Model):
    """
    Product brand/manufacturer model.
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    description = models.TextField(max_length=1000, blank=True)
    
    # Brand assets
    logo = models.ImageField(upload_to='brands/', null=True, blank=True)
    cover_image = models.ImageField(upload_to='brands/covers/', null=True, blank=True)
    website = models.URLField(max_length=200, blank=True)
    
    # Metadata
    is_active = models.BooleanField(default=True)
    featured = models.BooleanField(default=False)
    
    # Contact info
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(max_length=500, blank=True)
    
    # SEO
    meta_title = models.CharField(max_length=100, blank=True)
    meta_description = models.CharField(max_length=200, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['is_active', 'featured']),
        ]
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    @property
    def product_count(self):
        """Get count of active products from this brand."""
        return self.products.filter(is_active=True).count()


class Product(models.Model):
    """
    Main product model with all product details.
    """
    
    # Product status choices
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('pending', 'Pending Review'),
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('out_of_stock', 'Out of Stock'),
        ('discontinued', 'Discontinued'),
    )
    
    # Product type choices
    TYPE_CHOICES = (
        ('simple', 'Simple Product'),
        ('variable', 'Variable Product'),
        ('digital', 'Digital Product'),
        ('service', 'Service'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Basic information
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=250, unique=True, blank=True)
    sku = models.CharField(max_length=50, unique=True, help_text="Stock Keeping Unit")
    barcode = models.CharField(max_length=100, blank=True, help_text="UPC, EAN, etc.")
    
    # Relationships
    category = models.ForeignKey(
        Category, 
        on_delete=models.PROTECT, 
        related_name='products',
        help_text="Main category"
    )
    brand = models.ForeignKey(
        Brand, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='products'
    )
    seller = models.ForeignKey(
        User, 
        on_delete=models.PROTECT, 
        related_name='products',
        limit_choices_to={'user_type__in': ['seller', 'admin']}
    )
    
    # Product details
    description = models.TextField(max_length=5000)
    short_description = models.CharField(max_length=500, blank=True)
    product_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='simple')
    
    # Pricing
    regular_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(0)])
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Supplier cost")
    
    # Inventory
    stock_quantity = models.PositiveIntegerField(default=0)
    low_stock_threshold = models.PositiveIntegerField(default=5)
    track_inventory = models.BooleanField(default=True)
    allow_backorders = models.BooleanField(default=False)
    
    # Shipping
    weight = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True, help_text="Weight in kg")
    length = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True, help_text="Length in cm")
    width = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True, help_text="Width in cm")
    height = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True, help_text="Height in cm")
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    is_active = models.BooleanField(default=False)
    featured = models.BooleanField(default=False)
    
    # SEO
    meta_title = models.CharField(max_length=100, blank=True)
    meta_description = models.CharField(max_length=200, blank=True)
    meta_keywords = models.CharField(max_length=255, blank=True)
    
    # Product statistics
    views_count = models.PositiveIntegerField(default=0)
    sold_count = models.PositiveIntegerField(default=0)
    
    # Tax
    tax_class = models.CharField(max_length=50, default='standard')
    is_taxable = models.BooleanField(default=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['slug', 'is_active']),
            models.Index(fields=['category', 'status']),
            models.Index(fields=['brand', 'status']),
            models.Index(fields=['sku']),
            models.Index(fields=['-created_at']),
            models.Index(fields=['featured', 'is_active']),
        ]
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        """
        Auto-generate slug and handle timestamps.
        """
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while Product.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        
        # Set published date when status becomes active
        if self.status == 'active' and not self.published_at:
            self.published_at = timezone.now()
        
        super().save(*args, **kwargs)
    
    @property
    def current_price(self):
        """Get the current effective price (sale price if available)."""
        if self.sale_price and self.sale_price < self.regular_price:
            return self.sale_price
        return self.regular_price
    
    @property
    def discount_percentage(self):
        """Calculate discount percentage if on sale."""
        if self.sale_price and self.sale_price < self.regular_price:
            discount = ((self.regular_price - self.sale_price) / self.regular_price) * 100
            return round(discount, 2)
        return 0
    
    @property
    def in_stock(self):
        """Check if product is in stock."""
        if not self.track_inventory:
            return True
        return self.stock_quantity > 0 or self.allow_backorders
    
    @property
    def average_rating(self):
        """Calculate average rating from reviews."""
        reviews = self.reviews.filter(is_approved=True)
        if reviews.exists():
            return round(reviews.aggregate(models.Avg('rating'))['rating__avg'], 1)
        return 0
    
    @property
    def reviews_count(self):
        """Get count of approved reviews."""
        return self.reviews.filter(is_approved=True).count()


class ProductImage(models.Model):
    """
    Product images gallery model.
    Supports multiple images per product with ordering.
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    
    # Image
    image = models.ImageField(upload_to='products/')
    thumbnail = models.ImageField(upload_to='products/thumbnails/', null=True, blank=True)
    alt_text = models.CharField(max_length=200, blank=True, help_text="Alt text for accessibility")
    
    # Metadata
    is_primary = models.BooleanField(default=False, help_text="Main product image")
    order = models.PositiveIntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order', 'created_at']
        indexes = [
            models.Index(fields=['product', 'is_primary']),
        ]
    
    def __str__(self):
        return f"Image for {self.product.name}"
    
    def save(self, *args, **kwargs):
        """
        Ensure only one primary image per product.
        """
        if self.is_primary:
            ProductImage.objects.filter(product=self.product, is_primary=True).update(is_primary=False)
        super().save(*args, **kwargs)


class ProductVariant(models.Model):
    """
    Product variants for variable products (size, color, etc.).
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    
    # Variant attributes
    name = models.CharField(max_length=100)  # e.g., "Size M - Red"
    sku = models.CharField(max_length=50, unique=True)
    
    # Attributes as JSON for flexibility
    attributes = models.JSONField(default=dict, help_text="e.g., {'size': 'M', 'color': 'Red'}")
    
    # Pricing (if different from base product)
    price_adjustment = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    sale_price_adjustment = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Inventory
    stock_quantity = models.PositiveIntegerField(default=0)
    
    # Media
    image = models.ForeignKey(ProductImage, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['sku']),
            models.Index(fields=['product', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.product.name} - {self.name}"
    
    @property
    def price(self):
        """Get variant price."""
        return self.product.regular_price + self.price_adjustment
    
    @property
    def sale_price(self):
        """Get variant sale price."""
        if self.product.sale_price:
            return self.product.sale_price + self.sale_price_adjustment
        return None


class ProductReview(models.Model):
    """
    Product reviews and ratings by customers.
    """
    
    RATING_CHOICES = [(i, str(i)) for i in range(1, 6)]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    
    # Review content
    title = models.CharField(max_length=200)
    content = models.TextField(max_length=2000)
    rating = models.PositiveSmallIntegerField(choices=RATING_CHOICES)
    
    # Pros and cons (optional)
    pros = models.TextField(max_length=500, blank=True)
    cons = models.TextField(max_length=500, blank=True)
    
    # Media
    images = models.JSONField(default=list, blank=True, help_text="List of review image URLs")
    
    # Status
    is_approved = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    
    # Helpful counts
    helpful_count = models.PositiveIntegerField(default=0)
    not_helpful_count = models.PositiveIntegerField(default=0)
    
    # Moderation
    moderation_note = models.CharField(max_length=500, blank=True)
    moderated_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='moderated_reviews'
    )
    moderated_at = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['product', 'user']  # One review per user per product
        indexes = [
            models.Index(fields=['product', 'is_approved']),
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['rating']),
        ]
    
    def __str__(self):
        return f"Review by {self.user.email} for {self.product.name}"


class ProductReviewHelpful(models.Model):
    """
    Track which users found reviews helpful.
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    review = models.ForeignKey(ProductReview, on_delete=models.CASCADE, related_name='helpful_votes')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_helpful = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['review', 'user']
        indexes = [
            models.Index(fields=['review', 'user']),
        ]


class ProductTag(models.Model):
    """
    Product tags for better categorization and search.
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=60, unique=True, blank=True)
    products = models.ManyToManyField(Product, related_name='tags', blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class ProductAttribute(models.Model):
    """
    Product attributes (e.g., Size, Color, Material) for filtering.
    """
    
    ATTRIBUTE_TYPES = (
        ('text', 'Text'),
        ('number', 'Number'),
        ('color', 'Color'),
        ('select', 'Select'),
        ('multiselect', 'Multi Select'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50, unique=True)
    attribute_type = models.CharField(max_length=20, choices=ATTRIBUTE_TYPES, default='text')
    
    # For select/multiselect attributes
    options = models.JSONField(default=list, blank=True, help_text="List of possible values")
    
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order', 'name']
    
    def __str__(self):
        return self.name


class ProductAttributeValue(models.Model):
    """
    Values for product attributes.
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='attribute_values')
    attribute = models.ForeignKey(ProductAttribute, on_delete=models.CASCADE)
    value = models.CharField(max_length=255)  # The actual value
    extra_data = models.JSONField(default=dict, blank=True)  # e.g., color hex code
    
    class Meta:
        unique_together = ['product', 'attribute']
        indexes = [
            models.Index(fields=['attribute', 'value']),
        ]
    
    def __str__(self):
        return f"{self.attribute.name}: {self.value}"