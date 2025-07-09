from django.shortcuts import render, redirect, get_object_or_404
from datetime import date
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.http import JsonResponse
from django.db import transaction
import json
import logging
logger = logging.getLogger(__name__)
from django.contrib.auth.decorators import login_required
from .forms import RegisterForm, LoginForm, CheckoutForm, PasswordChangeForm, ContactForm
from .models import Profile, Categories, HostingPlan, Order, Newsletter, ContactForm as ContactFormModel, Logo, PromoCode
from blogs.models import Blog
import razorpay
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import validate_email as core_validate_email
from .formatters import PDFFormatter
from django.http import HttpResponse
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

@login_required
def update_profile(request):
    """Allow users to update their profile information."""
    user = request.user
    profile, created = Profile.objects.get_or_create(user=user)

    if request.method == 'POST':
        # Update user fields
        user.first_name = request.POST.get('first_name', '').strip()
        user.last_name = request.POST.get('last_name', '').strip()
        user.email = request.POST.get('email', '').strip()
        user.save()

        # Update profile fields
        profile.phone = request.POST.get('phone', '').strip()
        profile.address = request.POST.get('address', '').strip()
        profile.bio = request.POST.get('bio', '').strip()
        
        if 'avatar' in request.FILES:
            profile.avatar = request.FILES['avatar']
            
        profile.save()

        messages.success(request, 'Profile updated successfully.')
        return redirect('dashboard')

    context = {
        'user': user,
        'profile': profile,
    }
    return render(request, 'pages/dashboard.html', context)
@login_required
def change_password_view(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password was successfully updated!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'pages/dashboard.html', {
        'form': form
    })

@login_required
def update_notifications(request):
    if request.method == 'POST':
        # Logic to update notification settings
        messages.success(request, 'Notification settings updated.')
        return redirect('dashboard')
    return redirect('dashboard')

# Checkout Views
@login_required
def select_plan_for_checkout(request, plan_id, billing_cycle):
    """Select a hosting plan and store it in session for checkout"""
    plan = get_object_or_404(HostingPlan, id=plan_id)
    request.session['selected_plan_id'] = plan_id
    request.session['billing_cycle'] = billing_cycle
    return redirect('checkout')

@login_required
def checkout(request):
    """Handle checkout process with form validation and payment method selection"""
    plan_id = request.session.get('selected_plan_id')
    billing_cycle = request.session.get('billing_cycle', 'monthly')  # Default to monthly

    if not plan_id:
        messages.error(request, "No hosting plan selected. Please choose a plan first.")
        return redirect('home')

    plan = get_object_or_404(HostingPlan, id=plan_id)
    
    # Calculate pricing based on billing cycle
    if billing_cycle == 'yearly':
        subtotal = plan.yearly_price
        details = plan.yearly_details
    elif billing_cycle == 'quarterly':
        subtotal = plan.quarterly_price
        details = plan.quarterly_details
    elif billing_cycle == 'halfyearly':
        subtotal = plan.halfyearly_price
        details = plan.halfyearly_details
    elif billing_cycle == 'biannual':
        subtotal = plan.biannual_price
        details = plan.biannual_details
    elif billing_cycle == 'triannual':
        subtotal = plan.triannual_price
        details = plan.triannual_details
    else:
        subtotal = plan.monthly_price
        details = plan.monthly_details

    if subtotal is None:
        messages.error(request, f"The selected plan is not available for the '{billing_cycle}' billing cycle.")
        return redirect('home')

    plan.features = _parse_description(details)

    tax_rate = 18
    tax = (subtotal * tax_rate) / 100
    total = subtotal + tax

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            payment_method = form.cleaned_data.get('payment_method')
            promo_code_str = request.POST.get('promo_code')
            promo_code_obj = None
            discount_amount = 0

            if promo_code_str:
                try:
                    promo_code_obj = PromoCode.objects.get(code=promo_code_str)
                    if promo_code_obj.is_valid():
                        if promo_code_obj.discount_type == 'percentage':
                            discount_amount = (subtotal * promo_code_obj.discount_value) / 100
                        else:
                            discount_amount = promo_code_obj.discount_value
                        
                        new_subtotal = subtotal - discount_amount
                        tax = (new_subtotal * tax_rate) / 100
                        total = new_subtotal + tax
                    else:
                        messages.error(request, 'Invalid or expired promo code.')
                        promo_code_obj = None
                except PromoCode.DoesNotExist:
                    messages.error(request, 'Invalid promo code.')
                    promo_code_obj = None

            try:
                with transaction.atomic():
                    order = Order.objects.create(
                        user=request.user,
                        hosting_plan=plan,
                        total_amount=total,
                        promo_code=promo_code_obj,
                        discount_amount=discount_amount,
                        tax_amount=tax,
                        payment_method=payment_method,
                        first_name=form.cleaned_data['first_name'],
                        last_name=form.cleaned_data['last_name'],
                        email=form.cleaned_data['email'],
                        phone=form.cleaned_data['phone'],
                        domain_name=form.cleaned_data['domain_name'],
                        address=form.cleaned_data['address'],
                        city=form.cleaned_data['city'],
                        state=form.cleaned_data['state'],
                        zip_code=form.cleaned_data['zip_code'],
                        country=form.cleaned_data['country'],
                        gst_number=form.cleaned_data['gst_number'],
                        payment_status='pending',
                        billing_cycle=billing_cycle
                    )

                    if promo_code_obj:
                        promo_code_obj.usage_count += 1
                        promo_code_obj.save()

                    if payment_method == 'razorpay':
                        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
                        razorpay_order = client.order.create({
                            'amount': int(total * 100),
                            'currency': 'INR',
                            'receipt': f'order_{order.id}',
                        })
                        order.transaction_id = razorpay_order['id']
                        order.save()

                        return render(request, 'pages/razorpay_payment.html', {
                            'rzp_key_id': settings.RAZORPAY_KEY_ID,
                            'amount': int(total * 100),
                            'currency': 'INR',
                            'order_id': order.id,
                            'rzp_order_id': razorpay_order['id'],
                            'callback_url': request.build_absolute_uri(f'/razorpay-callback/'),
                            'prefill_name': f"{order.first_name} {order.last_name}",
                            'prefill_email': order.email,
                            'prefill_contact': order.phone,
                            'notes_address': order.address,
                        })
                    else:
                        messages.success(request, f"Order #{order.id} created successfully!")
                        return redirect('dashboard')

            except Exception as e:
                logger.error(f"Error during order creation: {e}")
                messages.error(request, "An error occurred during checkout. Please try again.")
        else:
            messages.error(request, "Please correct the form errors below.")
    else:
        form = CheckoutForm()
    
    context = {
        'form': form,
        'plan': plan,
        'subtotal': subtotal,
        'tax_rate': tax_rate,
        'tax': tax,
        'total': total,
    }
    return render(request, 'pages/checkout.html', context)
@login_required
def apply_promo_code(request):
    if request.method == 'POST':
        promo_code_str = request.POST.get('promo_code')
        if not promo_code_str:
            return JsonResponse({'status': 'error', 'message': 'Promo code is required.'}, status=400)

        try:
            promo_code = PromoCode.objects.get(code=promo_code_str)
            if promo_code.is_valid():
                return JsonResponse({
                    'status': 'success',
                    'discount_type': promo_code.discount_type,
                    'discount_value': promo_code.discount_value,
                })
            else:
                return JsonResponse({'status': 'error', 'message': 'Invalid or expired promo code.'}, status=404)
        except PromoCode.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Invalid promo code.'}, status=404)

    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=405)

# Razorpay callback (keep existing implementation)
@csrf_exempt
def razorpay_callback(request):
    """Handle Razorpay payment callback after successful/failed payment"""
    if request.method == "POST":
        try:
            # The request body contains the JSON data from the frontend
            data = json.loads(request.body)
            razorpay_order_id = data.get('razorpay_order_id')
            razorpay_payment_id = data.get('razorpay_payment_id')
            razorpay_signature = data.get('razorpay_signature')
            order_id = data.get('order_id')

            # Find the order using our internal order_id and verify the razorpay_order_id
            order = Order.objects.get(id=order_id, transaction_id=razorpay_order_id)

            # Verify the payment signature
            client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
            client.utility.verify_payment_signature({
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': razorpay_payment_id,
                'razorpay_signature': razorpay_signature
            })

            # Update order status to 'completed'
            order.payment_status = "completed"
            order.status = "processing"
            order.transaction_id = razorpay_payment_id  # Save the final payment ID
            order.save()


            # Send confirmation email in background
            import threading
            threading.Thread(target=send_order_confirmation_email, args=(order,)).start()

            # Clear session data
            if 'selected_plan_id' in request.session:
                del request.session['selected_plan_id']
            if 'billing_cycle' in request.session:
                del request.session['billing_cycle']

            # Return a JSON response to the frontend
            return JsonResponse({"status": "success", "order_id": order.id})

        except Order.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Order not found."}, status=404)
        except razorpay.errors.SignatureVerificationError:
            return JsonResponse({"status": "error", "message": "Payment verification failed."}, status=400)
        except Exception as e:
            logger.error(f"Error in Razorpay callback: {e}")
            return JsonResponse({"status": "error", "message": "An unexpected error occurred."}, status=500)

    # If not a POST request, return an error
    return JsonResponse({"status": "error", "message": "Invalid request method."}, status=405)

# Registration Form views
def register_view(request):
    logo = Logo.objects.first()
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        
        if form.is_valid():
            try:
                with transaction.atomic():
                    # Create new user
                    user = User.objects.create_user(
                        username=form.cleaned_data['email'],  # Using email as username
                        email=form.cleaned_data['email'],
                        password=form.cleaned_data['password'],
                        first_name=form.cleaned_data['first_name'],
                        last_name=form.cleaned_data['last_name'] or ''
                    )
                    
                    # Create or update user profile with phone number
                    profile, created = Profile.objects.get_or_create(user=user)
                    profile.phone = form.cleaned_data['phone']
                    profile.save()
                    
                    # Auto-login after registration if remember_me is checked
                    if form.cleaned_data.get('remember_me'):
                        login(request, user)
                        messages.success(request, 'Registration successful! You are now logged in.')
                        return redirect('home')  # Change 'dashboard' to 'home' or your desired redirect
                    else:
                        messages.success(request, 'Registration successful! Please login.')
                        return redirect('login')
                        
            except Exception as e:
                messages.error(request, f'An error occurred during registration: {str(e)}')
                
        else:
            # Form has errors - they will be displayed in the template
            messages.error(request, 'Please correct the errors below.')
    else:
        form = RegisterForm()
    
    return render(request, 'pages/register.html', {'form': form, 'logo': logo})

def thank_you(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    context = {
        'order': order,
    }
    return render(request, 'pages/thank_you.html', context)

# Dashboard View
def dashboard_view(request):
    user = request.user
    profile, created = Profile.objects.get_or_create(user=user)
    user_orders = Order.objects.filter(user=request.user).order_by('-created_at')
    
    # Password change form
    password_form = PasswordChangeForm(user)

    context = {
        'user': user,
        'profile': profile,
        'user_orders': user_orders,
        'password_form': password_form,
    }
    return render(request, 'pages/dashboard.html', context)

from django.contrib.auth import logout as django_logout

@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    try:
        category_slug = order.hosting_plan.categories.slug
        # Fetch all plans for this category (handle all possible return values)
        plans = get_plans_by_categories(category_slug)
        if len(plans) == 5:
            monthly_plans, quarterly_plans, halfyearly_plans, yearly_plans, categories = plans
        elif len(plans) == 4:
            monthly_plans, yearly_plans, quarterly_plans, categories = plans
            halfyearly_plans = []
        else:
            monthly_plans = yearly_plans = quarterly_plans = halfyearly_plans = []
            categories = None
    except Exception:
        monthly_plans = yearly_plans = quarterly_plans = halfyearly_plans = []
        categories = None

    # Parse features for the ordered plan
    billing_cycle = order.billing_cycle
    if billing_cycle == 'yearly':
        details = getattr(order.hosting_plan, 'yearly_details', '')
    elif billing_cycle == 'quarterly':
        details = getattr(order.hosting_plan, 'quarterly_details', '')
    elif billing_cycle == 'halfyearly':
        details = getattr(order.hosting_plan, 'halfyearly_details', '')
    elif billing_cycle == 'biannual':
        details = getattr(order.hosting_plan, 'biannual_details', '')
    elif billing_cycle == 'triannual':
        details = getattr(order.hosting_plan, 'triannual_details', '')
    else:
        details = getattr(order.hosting_plan, 'monthly_details', '')
    order.hosting_plan.features = _parse_description(details)

    context = {
        'order': order,
        'monthly_plans': monthly_plans,
        'quarterly_plans': quarterly_plans,
        'halfyearly_plans': halfyearly_plans,
        'yearly_plans': yearly_plans,
        'categories': categories,
    }
    return render(request, 'pages/order_detail.html', context)

@login_required
def download_invoice(request, order_id):
    """Generate and download an invoice for a specific order."""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    # Create a PDF using the custom formatter
    formatter = PDFFormatter(order)
    return formatter.get_response()

@login_required

def logout(request):
    django_logout(request)
    messages.info(request, 'You have been logged out successfully.')
    return redirect('login')

# Optional: AJAX validation view
def validate_email(request):
    email = request.GET.get('email', None)
    data = {
        'is_taken': User.objects.filter(email__iexact=email).exists()
    }
    return JsonResponse(data)

# Pages views
def home(request):
    try:
        blogs = Blog.objects.all().order_by('-created_at')[:3]
    except Exception:
        blogs = []
    # Show Linux Shared Hosting starting price on home page
    try:
        linux_shared_plans, _, _, _, _ = get_plans_by_categories('linux-shared-hosting') or ([], None, None, None, None)
        dedicated_plans, _, _, _, _ = get_plans_by_categories('dedicated-servers') or ([], None, None, None, None)
        vps_plans, _, _, _, _ = get_plans_by_categories('linux-vps') or ([], None, None, None, None)

        def get_monthly_price(plans):
            prices = [plan.monthly_price for plan in plans if getattr(plan, 'monthly_price', None) not in (None, 0)]
            return min(prices) if prices else None

        starting_price = {
            'linux_shared': f"₹{get_monthly_price(linux_shared_plans)}" if get_monthly_price(linux_shared_plans) is not None else '',
            'dedicated_server': f"₹{get_monthly_price(dedicated_plans)}" if get_monthly_price(dedicated_plans) is not None else '',
            'vps': f"₹{get_monthly_price(vps_plans)}" if get_monthly_price(vps_plans) is not None else '',
        }
    except Exception:
        starting_price = {'linux_shared': '', 'dedicated_server': '', 'vps': ''}
    context = {
        'blogs': blogs,
        'starting_price': starting_price,
    }
    return render(request, "pages/index.html", context)

def about(request):
    return render(request, "pages/about.html")

def contact(request):
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            message = 'Your message has been sent successfully!'
            tags = 'success'
            if is_ajax:
                return JsonResponse({'message': message, 'tags': tags})
            messages.success(request, message)
            return redirect('contact')
        else:
            message = 'Please correct the errors below.'
            tags = 'error'
            if is_ajax:
                # This part needs to be improved to return form errors
                return JsonResponse({'message': message, 'tags': tags}, status=400)
            messages.error(request, message)
    else:
        form = ContactForm()
    return render(request, "pages/contact.html", {'form': form})

def faqs(request):
    return render(request, "pages/faqs.html")

# Blog views
def blog(request):
    return render(request, "pages/blog.html")

# Admin views 
def login_view(request):
    logo = Logo.objects.first()
    if request.user.is_authenticated:
        return redirect('home')  # Redirect if already logged in
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        
        if form.is_valid():
            user = form.cleaned_data['user']
            login(request, user)
            
            # Set session expiry based on remember_me
            if not form.cleaned_data.get('remember_me'):
                request.session.set_expiry(0)  # Browser session only
            else:
                request.session.set_expiry(1209600)  # 2 weeks
            
            messages.success(request, 'Login successful!')
            
            # Redirect to next page or home
            next_page = request.GET.get('next', 'home')
            return redirect(next_page)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = LoginForm()
    
    return render(request, "pages/login.html", {'form': form, 'logo': logo})

def register(request):
    # This should redirect to the actual register_view
    return redirect('register_view')

def _parse_description(description):
    """Helper function to parse plan descriptions into a dictionary."""
    if not description:
        return {}
    
    features = {}
    for line in description.strip().split('\n'):
        if '=' in line:
            key, value = line.split('=', 1)
            features[key.strip()] = value.strip()
    return features

def get_plans_by_categories(categories_slug):
    """Helper function to get plans by categories"""
    try:
        categories = Categories.objects.get(slug=categories_slug)
        plans = HostingPlan.objects.filter(
            categories=categories,
            is_active=True
        ).order_by('monthly_price')

        for plan in plans:
            plan.monthly_features = _parse_description(getattr(plan, 'monthly_details', ''))
            plan.quarterly_features = _parse_description(getattr(plan, 'quarterly_details', ''))
            plan.halfyearly_features = _parse_description(getattr(plan, 'halfyearly_details', ''))
            plan.yearly_features = _parse_description(getattr(plan, 'yearly_details', ''))

        monthly_plans = [p for p in plans if getattr(p, 'monthly_price', None) is not None]
        quarterly_plans = [p for p in plans if getattr(p, 'quarterly_price', None) is not None]
        halfyearly_plans = [p for p in plans if getattr(p, 'halfyearly_price', None) is not None]
        yearly_plans = [p for p in plans if getattr(p, 'yearly_price', None) is not None]

        return monthly_plans, quarterly_plans, halfyearly_plans, yearly_plans, categories
    except Categories.DoesNotExist:
        return (HostingPlan.objects.none(),) * 5

# Hosting services views
def dedicated_servers(request):
    monthly_plans, quarterly_plans, halfyearly_plans, yearly_plans, categories = get_plans_by_categories('dedicated-servers')
    
    starting_price = None
    if monthly_plans:
        starting_price = min(plan.monthly_price for plan in monthly_plans)
        
    context = {
        'monthly_plans': monthly_plans,
        'quarterly_plans': quarterly_plans,
        'halfyearly_plans': halfyearly_plans,
        'yearly_plans': yearly_plans,
        'categories': categories,
        'page_title': 'Dedicated Servers',
        'starting_price': starting_price
    }
    return render(request, 'pages/dedicated_servers.html', context)

def linux_vps(request):
    monthly_plans, quarterly_plans, halfyearly_plans, yearly_plans, categories = get_plans_by_categories('linux-vps')

    starting_price = None
    if monthly_plans:
        starting_price = min(plan.monthly_price for plan in monthly_plans)

    context = {
        'monthly_plans': monthly_plans,
        'quarterly_plans': quarterly_plans,
        'halfyearly_plans': halfyearly_plans,
        'yearly_plans': yearly_plans,
        'categories': categories,
        'page_title': 'Linux VPS',
        'starting_price': starting_price
    }
    return render(request, 'pages/linux_vps.html', context)

def linux_shared_hosting(request):
    try:
        categories = Categories.objects.get(slug='linux-shared-hosting')
        all_plans = HostingPlan.objects.filter(categories=categories, is_active=True).order_by('monthly_price')
    except Categories.DoesNotExist:
        categories = None
        all_plans = HostingPlan.objects.none()

    for plan in all_plans:
        plan.monthly_features = _parse_description(plan.monthly_details)
        plan.quarterly_features = _parse_description(plan.quarterly_details)
        plan.yearly_features = _parse_description(plan.yearly_details)
        plan.biannual_features = _parse_description(getattr(plan, 'biannual_details', ''))
        plan.triannual_features = _parse_description(getattr(plan, 'triannual_details', ''))

    monthly_plans = [p for p in all_plans if p.monthly_price is not None]
    quarterly_plans = [p for p in all_plans if p.quarterly_price is not None]
    yearly_plans = [p for p in all_plans if p.yearly_price is not None]
    biannual_plans = [p for p in all_plans if p.biannual_price is not None]
    triannual_plans = [p for p in all_plans if p.triannual_price is not None]

    starting_price = None
    if monthly_plans:
        starting_price = min((p.monthly_price for p in monthly_plans if p.monthly_price is not None), default=0)

    context = {
        'monthly_plans': monthly_plans,
        'quarterly_plans': quarterly_plans,
        'yearly_plans': yearly_plans,
        'biannual_plans': biannual_plans,
        'triannual_plans': triannual_plans,
        'categories': categories,
        'page_title': 'Linux Shared Hosting',
        'starting_price': starting_price
    }
    return render(request, 'pages/linux_shared_hosting.html', context)

def wordpress_shared_hosting(request):
    try:
        categories = Categories.objects.get(slug='wordpress-shared-hosting')
        all_plans = HostingPlan.objects.filter(categories=categories, is_active=True).order_by('monthly_price')
    except Categories.DoesNotExist:
        categories = None
        all_plans = HostingPlan.objects.none()

    for plan in all_plans:
        plan.monthly_features = _parse_description(plan.monthly_details)
        plan.quarterly_features = _parse_description(plan.quarterly_details)
        plan.yearly_features = _parse_description(plan.yearly_details)
        plan.biannual_features = _parse_description(getattr(plan, 'biannual_details', ''))
        plan.triannual_features = _parse_description(getattr(plan, 'triannual_details', ''))

    monthly_plans = [p for p in all_plans if p.monthly_price is not None]
    quarterly_plans = [p for p in all_plans if p.quarterly_price is not None]
    yearly_plans = [p for p in all_plans if p.yearly_price is not None]
    biannual_plans = [p for p in all_plans if p.biannual_price is not None]
    triannual_plans = [p for p in all_plans if p.triannual_price is not None]

    starting_price = None
    if monthly_plans:
        starting_price = min((p.monthly_price for p in monthly_plans if p.monthly_price is not None), default=0)

    context = {
        'monthly_plans': monthly_plans,
        'quarterly_plans': quarterly_plans,
        'yearly_plans': yearly_plans,
        'biannual_plans': biannual_plans,
        'triannual_plans': triannual_plans,
        'categories': categories,
        'page_title': 'Wordpress Shared Hosting',
        'starting_price': starting_price
    }
    return render(request, 'pages/wordpress_shared_hosting.html', context)

def linux_reseller_hosting(request):
    try:
        monthly_plans, quarterly_plans, halfyearly_plans, yearly_plans, categories = get_plans_by_categories('linux-reseller-hosting')
    except Exception:
        monthly_plans = quarterly_plans = halfyearly_plans = yearly_plans = []
        categories = None

    starting_price = None
    if monthly_plans:
        starting_price = min((p.monthly_price for p in monthly_plans if p.monthly_price is not None), default=0)

    context = {
        'monthly_plans': monthly_plans,
        'quarterly_plans': quarterly_plans,
        'halfyearly_plans': halfyearly_plans,
        'yearly_plans': yearly_plans,
        'categories': categories,
        'page_title': 'Linux Reseller Hosting',
        'starting_price': starting_price
    }
    return render(request, 'pages/linux_reseller_hosting.html', context)

def wordpress_reseller_hosting(request):
    try:
        monthly_plans, quarterly_plans, halfyearly_plans, yearly_plans, categories = get_plans_by_categories('wordpress-reseller-hosting')
    except Exception:
        monthly_plans = quarterly_plans = halfyearly_plans = yearly_plans = []
        categories = None

    starting_price = None
    if monthly_plans:
        starting_price = min((p.monthly_price for p in monthly_plans if p.monthly_price is not None), default=0)

    context = {
        'monthly_plans': monthly_plans,
        'quarterly_plans': quarterly_plans,
        'halfyearly_plans': halfyearly_plans,
        'yearly_plans': yearly_plans,
        'categories': categories,
        'page_title': 'Wordpress Reseller Hosting',
        'starting_price': starting_price
    }
    return render(request, 'pages/wordpress_reseller_hosting.html', context)

# Legal views 
def terms_of_service(request):
    return render(request, "pages/terms_of_service.html")

def privacy_policy(request):
    return render(request, "pages/privacy_policy.html")

def legal(request):
    return render(request, "pages/legal.html")

def subscribe_email(request):
    if request.method == "POST":
        email = request.POST.get("email")
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

        if not email:
            message = "Please enter an email address."
            tags = "error"
            if is_ajax:
                return JsonResponse({'message': message, 'tags': tags}, status=400)
            messages.error(request, message)
            return redirect(request.META.get('HTTP_REFERER', '/'))

        try:
            core_validate_email(email)
        except ValidationError:
            message = "Please enter a valid email address."
            tags = "error"
            if is_ajax:
                return JsonResponse({'message': message, 'tags': tags}, status=400)
            messages.error(request, message)
            return redirect(request.META.get('HTTP_REFERER', '/'))

        try:
            subscribe_obj, created = Newsletter.objects.get_or_create(email=email)
            if created:
                message = "Thank you for subscribing!"
                tags = "success"
            else:
                message = "You are already subscribed with this email address."
                tags = "info"
        except Exception as e:
            message = "An error occurred. Please try again."
            tags = "error"

        if is_ajax:
            return JsonResponse({'message': message, 'tags': tags})
        
        messages.add_message(request, messages.SUCCESS if tags == 'success' else (messages.INFO if tags == 'info' else messages.ERROR), message)
        return redirect(request.META.get('HTTP_REFERER', '/'))

    return redirect(request.META.get('HTTP_REFERER', '/'))
def send_order_confirmation_email(order):
    """Sends a confirmation email to the user and a notification to the admin."""
    from .models import Logo, BillingConfig
    # Prepare context for the invoice template
    billing_cycle = order.billing_cycle
    if billing_cycle == 'yearly':
        details = order.hosting_plan.yearly_details
    elif billing_cycle == 'quarterly':
        details = order.hosting_plan.quarterly_details
    else:
        details = order.hosting_plan.monthly_details
    
    # Parse plan features
    def _parse_description(description):
        if not description:
            return {}
        features = {}
        for line in description.strip().split('\n'):
            if '=' in line:
                key, value = line.split('=', 1)
                features[key.strip()] = value.strip()
        return features
    plan_details = _parse_description(details)

    # Billing address
    billing_address = {
        'name': f"{order.first_name} {order.last_name}",
        'address': order.address,
        'city': order.city,
        'state': order.state,
        'zip_code': order.zip_code,
        'country': order.country,
        'email': order.email,
        'phone': order.phone,
    }
    # Billing config and logo
    logo = Logo.objects.first()
    billing_config = BillingConfig.objects.first()

    # Calculate subtotal for display
    subtotal = order.total_amount - order.tax_amount + order.discount_amount

    # Prepare context for the template
    context = {
        'order': order,
        'invoice': order,  # For template compatibility
        'plan': order.hosting_plan,
        'plan_details': plan_details,
        'subtotal': subtotal,
        'billing_address': billing_address,
        'logo': logo,
        'billing_config': billing_config,
        'payment_method': order.payment_method,
        'transaction_id': order.transaction_id,
    }

    # Render the HTML email template
    html_message = render_to_string('invoicing/invoice_template.html', context)
    plain_message = strip_tags(html_message)

    user_subject = f"Your Dost Host Order Confirmation #{order.id}"
    admin_subject = f"New Order Received #{order.id}"

    # Send email to the user
    send_mail(
        user_subject,
        plain_message,
        settings.DEFAULT_FROM_EMAIL,
        [order.email],
        html_message=html_message,
        fail_silently=False,
    )
    # Send email to the admin
    send_mail(
        admin_subject,
        f"A new order has been placed by {order.user.username}. Order ID: {order.id}",
        settings.DEFAULT_FROM_EMAIL,
        ['info@dost.host'],  # Replace with your admin email
        fail_silently=False,
    )