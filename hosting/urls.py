"""
URL configuration for dosthost project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from hosting import views

urlpatterns = [

    # Pages URLs
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('faqs/', views.faqs, name='faqs'),

    # Blog URLs

    # Admin URL
    path('accounts/login/', views.login_view, name='login'),
    path('accounts/register/', views.register_view, name='register_view'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('logout/', views.logout, name='logout'),
    path('change-password/', views.change_password_view, name='change_password'),
    path('update-notifications/', views.update_notifications, name='update_notifications'),
    path('order-detail/<int:order_id>/', views.order_detail, name='order_detail'),
path('download-invoice/<int:order_id>/', views.download_invoice, name='download_invoice'),
    path('update-profile/', views.update_profile, name='update_profile'),

    # Hosting services URLs
    path('dedicated-servers/', views.dedicated_servers, name='dedicated-servers'),
    path('linux-vps/', views.linux_vps, name='linux-vps'),
    path('linux-shared-hosting/', views.linux_shared_hosting, name='linux-shared-hosting'),
    path('wordpress-shared-hosting/', views.wordpress_shared_hosting, name='wordpress-shared-hosting'),
    path('linux-reseller-hosting/', views.linux_reseller_hosting, name='linux-reseller-hosting'),
    path('wordpress-reseller-hosting/', views.wordpress_reseller_hosting, name='wordpress-reseller-hosting'),
    path('select-plan/<int:plan_id>/<str:billing_cycle>/', views.select_plan_for_checkout, name='select_plan_for_checkout'),
    path('checkout/', views.checkout, name='checkout'),
    path('razorpay-callback/', views.razorpay_callback, name='razorpay_callback'),
    path('apply-promo-code/', views.apply_promo_code, name='apply_promo_code'),
    path('thank-you/<int:order_id>/', views.thank_you, name='thank_you'),
    
    # Legal URLs
    path('terms-of-service/', views.terms_of_service, name='terms-of-service'),
    path('privacy-policy/', views.privacy_policy, name='privacy-policy'),
    path('legal/', views.legal, name='legal'),

    # Subscribe
    path('subscribe/',views.subscribe_email, name='subscribe'),
    
]

