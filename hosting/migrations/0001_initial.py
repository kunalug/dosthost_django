# Generated by Django 5.2.1 on 2025-07-01 08:40

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='BillingConfig',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('from_name', models.CharField(blank=True, max_length=100, null=True)),
                ('from_address', models.TextField(blank=True, null=True)),
                ('from_email', models.EmailField(blank=True, max_length=254, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Categories',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('slug', models.SlugField(max_length=120, unique=True)),
                ('description', models.TextField(blank=True)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name_plural': 'Categories',
            },
        ),
        migrations.CreateModel(
            name='ContactForm',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=254)),
                ('subject', models.CharField(max_length=200)),
                ('message', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Footer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('facebook_url', models.URLField(blank=True, null=True)),
                ('twitter_url', models.URLField(blank=True, null=True)),
                ('linkedin_url', models.URLField(blank=True, null=True)),
                ('instagram_url', models.URLField(blank=True, null=True)),
                ('is_active', models.BooleanField(default=True)),
            ],
            options={
                'verbose_name_plural': 'Footer Social Media Links',
            },
        ),
        migrations.CreateModel(
            name='Logo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('image', models.ImageField(upload_to='logos/')),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('desktop_logo', models.ImageField(blank=True, null=True, upload_to='logos/desktop/')),
                ('mobile_logo', models.ImageField(blank=True, null=True, upload_to='logos/mobile/')),
                ('favicon', models.ImageField(blank=True, null=True, upload_to='logos/favicon/')),
                ('footer_logo', models.ImageField(blank=True, null=True, upload_to='logos/footer/')),
                ('sidebar_logo', models.ImageField(blank=True, null=True, upload_to='logos/sidebar/')),
                ('auth_logo', models.ImageField(blank=True, null=True, upload_to='logos/auth/')),
                ('bill_logo', models.ImageField(blank=True, null=True, upload_to='logos/bill/')),
            ],
        ),
        migrations.CreateModel(
            name='Newsletter',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('is_active', models.BooleanField(default=True)),
                ('subscribed_at', models.DateTimeField(auto_now_add=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='PromoCode',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=50, unique=True)),
                ('discount_type', models.CharField(choices=[('percentage', 'Percentage'), ('fixed', 'Fixed Price')], default='percentage', max_length=10)),
                ('discount_value', models.DecimalField(decimal_places=2, help_text='The discount value, either as a percentage or a fixed amount.', max_digits=10)),
                ('usage_limit', models.PositiveIntegerField(default=1, help_text='How many times this promo code can be used.')),
                ('usage_count', models.PositiveIntegerField(default=0, editable=False, help_text='How many times this promo code has been used.')),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='HostingPlan',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('slug', models.SlugField(blank=True, help_text='Unique slug for URL, auto-generated from title if not provided.', max_length=220, unique=True)),
                ('monthly_price', models.DecimalField(blank=True, decimal_places=2, help_text='Monthly plan price', max_digits=10, null=True)),
                ('quarterly_price', models.DecimalField(blank=True, decimal_places=2, help_text='Quarterly plan price', max_digits=10, null=True)),
                ('yearly_price', models.DecimalField(blank=True, decimal_places=2, help_text='Yearly plan price', max_digits=10, null=True)),
                ('monthly_details', models.TextField(blank=True, help_text='Details for the monthly plan', null=True)),
                ('quarterly_details', models.TextField(blank=True, help_text='Details for the quarterly plan', null=True)),
                ('yearly_details', models.TextField(blank=True, help_text='Details for the yearly plan', null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('categories', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='plans', to='hosting.categories')),
            ],
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=50)),
                ('last_name', models.CharField(max_length=50)),
                ('email', models.EmailField(max_length=254)),
                ('phone', models.CharField(max_length=20)),
                ('address', models.TextField()),
                ('city', models.CharField(max_length=100)),
                ('state', models.CharField(max_length=100)),
                ('country', models.CharField(max_length=100)),
                ('zip_code', models.CharField(max_length=10)),
                ('domain_name', models.CharField(blank=True, max_length=255, null=True)),
                ('gst_number', models.CharField(blank=True, max_length=15, null=True)),
                ('total_amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('discount_amount', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('tax_amount', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('processing', 'Processing'), ('completed', 'Completed'), ('cancelled', 'Cancelled'), ('failed', 'Failed')], default='pending', max_length=20)),
                ('billing_cycle', models.CharField(choices=[('monthly', 'Monthly'), ('quarterly', 'Quarterly'), ('yearly', 'Yearly')], default='monthly', max_length=20)),
                ('payment_method', models.CharField(blank=True, max_length=50, null=True)),
                ('payment_status', models.CharField(choices=[('processing', 'Processing'), ('completed', 'Completed'), ('failed', 'Failed'), ('pending', 'Pending')], default='processing', max_length=20)),
                ('transaction_id', models.CharField(blank=True, max_length=100, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('hosting_plan', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='orders', to='hosting.hostingplan')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='orders', to=settings.AUTH_USER_MODEL)),
                ('promo_code', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='orders', to='hosting.promocode')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='PaymentDetails',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('payment_method', models.CharField(choices=[('credit_card', 'Credit Card'), ('debit_card', 'Debit Card'), ('paypal', 'PayPal'), ('bank_transfer', 'Bank Transfer'), ('crypto', 'Cryptocurrency')], max_length=20)),
                ('payment_gateway', models.CharField(blank=True, max_length=50, null=True)),
                ('gateway_transaction_id', models.CharField(blank=True, max_length=100, null=True)),
                ('payment_amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('payment_currency', models.CharField(default='USD', max_length=3)),
                ('payment_date', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(choices=[('processing', 'Processing'), ('completed', 'Completed'), ('failed', 'Failed'), ('pending', 'Pending')], default='processing', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('paid_at', models.DateTimeField(blank=True, null=True)),
                ('payment_id', models.CharField(blank=True, max_length=100, null=True)),
                ('amount', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('order', models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='payment_details', to='hosting.order')),
            ],
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone', models.CharField(blank=True, max_length=20, null=True)),
                ('address', models.TextField(blank=True, null=True)),
                ('city', models.CharField(blank=True, max_length=100, null=True)),
                ('state', models.CharField(blank=True, max_length=100, null=True)),
                ('country', models.CharField(blank=True, max_length=100, null=True)),
                ('zip_code', models.CharField(blank=True, max_length=10, null=True)),
                ('bio', models.TextField(blank=True, null=True)),
                ('avatar', models.ImageField(blank=True, null=True, upload_to='avatars/')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
