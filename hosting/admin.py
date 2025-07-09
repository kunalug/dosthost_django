from django.contrib import admin
from .models import HostingPlan, Categories, Order, Logo, Newsletter, Profile, Footer, ContactForm, PromoCode, BillingConfig

@admin.register(HostingPlan)
class HostingPlanAdmin(admin.ModelAdmin):
    list_display = ('title', 'monthly_price', 'quarterly_price', 'yearly_price', 'is_active', 'slug', 'categories')
    list_filter = ('is_active', 'categories')
    search_fields = ('title', 'slug')
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ('monthly_price', 'quarterly_price', 'yearly_price', 'is_active')

# Categories
@admin.register(Categories)
class HostingCategoriesAdmin(admin.ModelAdmin):
    # list_display = ('name', 'slug', 'icon_class')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}

# Orders
@admin.register(Order)
class HostingOrdersAdmin(admin.ModelAdmin):
    # Update the fields below to match actual fields on Order model
    list_display = ('id', 'user', 'hosting_plan', 'total_amount', 'status', 'payment_status', 'created_at')
    list_filter = ('status', 'payment_status', 'created_at', 'hosting_plan')
    list_editable = ('status', 'payment_status')
    raw_id_fields = ('user', 'hosting_plan', 'promo_code')
    search_fields = ('user__username', 'hosting_plan__title', 'id')
    
@admin.register(Logo)
class LogoAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'created_at')
    fieldsets = (
        ('Basic Info', {
            'fields': ('name', 'image', 'is_active')
        }),
        ('Desktop Logos', {
            'fields': ('desktop_logo',)
        }),
        ('Mobile Logos', {
            'fields': ('mobile_logo',)
        }),
        ('Favicon', {
            'fields': ('favicon',)
        }),
        ('Footer Logo', {
            'fields': ('footer_logo',)
        }),
        ('Sidebar Logo', {
            'fields': ('sidebar_logo',)
        }),
        ('Auth Logo', {
            'fields': ('auth_logo',)
        }),
        ('Bill Logo', {
            'fields': ('bill_logo',)
        }),
    )
    
# Newsletter
@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    list_display = ('email', 'created_at')
    search_fields = ('email',)

# Payments

# Profile
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'address', 'created_at')
    search_fields = ('user__username', 'phone', 'address')
    list_filter = ('created_at',)

@admin.register(Footer)
class FooterAdmin(admin.ModelAdmin):
    list_display = ('facebook_url', 'twitter_url', 'linkedin_url', 'instagram_url', 'is_active')
    list_editable = ('is_active',)

@admin.register(ContactForm)
class ContactFormAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'created_at')
    search_fields = ('name', 'email', 'subject')
    list_filter = ('created_at',)
from .models import PromoCode

@admin.register(PromoCode)
class PromoCodeAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount_type', 'discount_value', 'usage_limit', 'usage_count', 'is_active', 'created_at')
    list_filter = ('is_active', 'discount_type')
    search_fields = ('code',)
    list_editable = ('discount_value', 'usage_limit', 'is_active')
    readonly_fields = ('usage_count',)

@admin.register(BillingConfig)
class BillingConfigAdmin(admin.ModelAdmin):
    list_display = ('from_name', 'from_email', 'from_address')
    list_editable = ('from_email', 'from_address')