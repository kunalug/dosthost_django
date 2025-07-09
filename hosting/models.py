from django.db import models
from django.contrib.auth.models import User
from django.contrib import admin

# Profile Model
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    zip_code = models.CharField(max_length=10, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

# Categories
class Categories(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=120, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Categories"
    
    def __str__(self):
        return self.name

# Hosting Plan Model
class HostingPlan(models.Model):
    PLAN_TYPES = [
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('halfyearly', 'Half Yearly'),
        ('yearly', 'Yearly'),
        ('biannual', 'Biannual'),
        ('triannual', 'Triannual'),
    ]
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True, help_text="Unique slug for URL, auto-generated from title if not provided.")
    categories = models.ForeignKey(
        Categories,
        on_delete=models.CASCADE,
        related_name='plans',
        null=True,
        blank=True
    )

    # Add fields for different plan durations and their prices
    monthly_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, help_text="Monthly plan price")
    quarterly_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, help_text="Quarterly plan price")
    halfyearly_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, help_text="Half Yearly plan price")
    yearly_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, help_text="Yearly plan price")
    biannual_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, help_text="Biannual plan price")
    triannual_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, help_text="Triannual plan price")
    monthly_details = models.TextField(blank=True, null=True, help_text="Details for the monthly plan")
    quarterly_details = models.TextField(blank=True, null=True, help_text="Details for the quarterly plan")
    halfyearly_details = models.TextField(blank=True, null=True, help_text="Details for the half yearly plan")
    yearly_details = models.TextField(blank=True, null=True, help_text="Details for the yearly plan")
    biannual_details = models.TextField(blank=True, null=True, help_text="Details for the biannual plan")
    triannual_details = models.TextField(blank=True, null=True, help_text="Details for the triannual plan")


    is_active = models.BooleanField(default=True)

# Order Model - Updated with all required fields
class Order(models.Model):
    ORDER_STATUS = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('failed', 'Failed'),
    ]

    PAYMENT_STATUS_CHOICES = [
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('pending', 'Pending'),
    ]

    # User Information
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='orders')
    
    # Personal Information
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    
    # Address Information
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=10)
    
    # Domain Information
    domain_name = models.CharField(max_length=255, blank=True, null=True)
    gst_number = models.CharField(max_length=15, blank=True, null=True)
    
    # Order Information
    hosting_plan = models.ForeignKey(HostingPlan, on_delete=models.SET_NULL, null=True, related_name='orders')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=ORDER_STATUS, default='pending')
    billing_cycle = models.CharField(max_length=20, choices=HostingPlan.PLAN_TYPES, default='monthly')
    
    promo_code = models.ForeignKey('PromoCode', on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    # Payment Information
    payment_method = models.CharField(max_length=50, blank=True, null=True)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='processing')
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Order #{self.id} - {self.user.username if self.user else '[No User]'} - {self.hosting_plan.title if self.hosting_plan else '[No Plan]'}"

#  Logo 
class Logo(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='logos/')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Desktop logos
    desktop_logo = models.ImageField(upload_to='logos/desktop/', blank=True, null=True)
    
    # Mobile logos
    mobile_logo = models.ImageField(upload_to='logos/mobile/', blank=True, null=True)
    
    # Favicon
    favicon = models.ImageField(upload_to='logos/favicon/', blank=True, null=True)

    # Footer Logo
    footer_logo = models.ImageField(upload_to='logos/footer/', blank=True, null=True)

    # Sidebar Logo
    sidebar_logo = models.ImageField(upload_to='logos/sidebar/', blank=True, null=True)

    # Auth Logo
    auth_logo = models.ImageField(upload_to='logos/auth/', blank=True, null=True)

    bill_logo = models.ImageField(upload_to='logos/bill/', blank=True, null=True)

    def __str__(self):
        return self.name


class BillingConfig(models.Model):
    from_name = models.CharField(max_length=100, blank=True, null=True)
    from_address = models.TextField(blank=True, null=True)
    from_email = models.EmailField(blank=True, null=True)

    def __str__(self):
        return "Billing Configuration"
    
# Newletter    
class Newsletter(models.Model):
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)  # Added created_at field
    
    def __str__(self):
        return self.email

#Payment Details    
class PaymentDetails(models.Model):
    PAYMENT_METHODS = [
        ('credit_card', 'Credit Card'),
        ('debit_card', 'Debit Card'),
        ('paypal', 'PayPal'),
        ('bank_transfer', 'Bank Transfer'),
        ('crypto', 'Cryptocurrency'),
    ]
    
    order = models.OneToOneField('Order', on_delete=models.SET_NULL, null=True, related_name='payment_details')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    payment_gateway = models.CharField(max_length=50, blank=True, null=True)
    gateway_transaction_id = models.CharField(max_length=100, blank=True, null=True)
    payment_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_currency = models.CharField(max_length=3, default='USD')
    payment_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=Order.PAYMENT_STATUS_CHOICES, default='processing')
    created_at = models.DateTimeField(auto_now_add=True)  # Added created_at field
    paid_at = models.DateTimeField(blank=True, null=True)  # Added paid_at field
    payment_id = models.CharField(max_length=100, blank=True, null=True)  # Added payment_id field
    amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)  # Added amount field

class Footer(models.Model):
    facebook_url = models.URLField(blank=True, null=True)
    twitter_url = models.URLField(blank=True, null=True)
    linkedin_url = models.URLField(blank=True, null=True)
    instagram_url = models.URLField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return "Footer Social Media Links"

    class Meta:
        verbose_name_plural = "Footer Social Media Links"

# Contact Form Model
class ContactForm(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.subject

# Promo Code Model
class PromoCode(models.Model):
    DISCOUNT_TYPE_CHOICES = [
        ('percentage', 'Percentage'),
        ('fixed', 'Fixed Price'),
    ]

    code = models.CharField(max_length=50, unique=True)
    discount_type = models.CharField(max_length=10, choices=DISCOUNT_TYPE_CHOICES, default='percentage')
    discount_value = models.DecimalField(max_digits=10, decimal_places=2, help_text="The discount value, either as a percentage or a fixed amount.")
    usage_limit = models.PositiveIntegerField(default=1, help_text="How many times this promo code can be used.")
    usage_count = models.PositiveIntegerField(default=0, editable=False, help_text="How many times this promo code has been used.")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.code

    def is_valid(self):
        """Check if the promo code is still valid."""
        return self.is_active and self.usage_count < self.usage_limit
