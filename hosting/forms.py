# forms.py
from django import forms
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.contrib.auth import authenticate
from .models import Order

# Checkout Form
class CheckoutForm(forms.ModelForm):
    payment_method = forms.ChoiceField(
        choices=[('razorpay', 'Razorpay')],
        widget=forms.RadioSelect,
        initial='razorpay'
    )
    
    
    promo_code = forms.CharField(
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter promo code'
        })
    )

    class Meta:
        model = Order
        fields = [
            'first_name', 'last_name', 'email', 'phone',
            'address', 'city', 'state', 'zip_code', 'country', 'gst_number', 'domain_name', 'payment_method'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'First Name*',
                'required': True
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Last Name*',
                'required': True
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Email*',
                'required': True
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Phone*',
                'required': True
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Address*',
                'required': True
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'City*',
                'required': True
            }),
            'state': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'State*',
                'required': True
            }),
            'zip_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Zip Code*',
                'required': True
            }),
            'country': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Country*',
                'required': True,
                'value': 'India'
            }),
            'domain_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Domain Name (e.g., example.com)',
                'required': False
            }),
            'gst_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'GST Number (Optional)',
            }),
        }
    
# Login Form
class LoginForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control ms-0',
            'placeholder': 'Enter your Email',
            'required': True,
            'autocomplete': 'username',
            'autocorrect': 'off',
            'autocapitalize': 'none'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control ms-0',
            'placeholder': 'Enter your Password',
            'required': True,
            'autocomplete': 'current-password',
            'data-lpignore': 'true',  # Prevents LastPass autofill
            'data-form-type': 'other'  # Additional protection against autofill
        })
    )
    
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control ms-0 border-end-0',
            'placeholder': 'Enter your Password',
            'required': True,
            'id': 'password'
        })
    )
    
    remember_me = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )
    
    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')
        
        if email and password:
            # Try to authenticate user using email as username
            user = authenticate(username=email, password=password)
            if user is None:
                raise forms.ValidationError("Invalid email or password.")
            elif not user.is_active:
                raise forms.ValidationError("This account has been deactivated.")
            
            # Store the user in cleaned_data for use in the view
            cleaned_data['user'] = user
        
        return cleaned_data
    
# Register Form
class RegisterForm(forms.Form):
    first_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={
            'class': 'form-control ms-0',
            'placeholder': 'Enter First Name',
            'required': True
        })
    )
    
    last_name = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control ms-0',
            'placeholder': 'Enter Last Name'
        })
    )
    
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control ms-0',
            'placeholder': 'Enter your Email',
            'required': True
        })
    )
    
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    
    phone = forms.CharField(
        validators=[phone_regex],
        max_length=17,
        widget=forms.TextInput(attrs={
            'class': 'form-control ms-0',
            'placeholder': 'Enter Mobile Number',
            'required': True
        })
    )
    
    password = forms.CharField(
        min_length=8,
        widget=forms.PasswordInput(attrs={
            'autocomplete': 'new-password',
            'class': 'form-control ms-0 border-end-0',
            'placeholder': 'Create a Password',
            'required': True,
            'id': 'id_password'
        })
    )
    
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control ms-0 border-end-0',
            'placeholder': 'Confirm Password',
            'required': True,
            'id': 'id_confirm_password'
        })
    )
    
    remember_me = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )
    
    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email address is already registered.")
        return email
    
    def clean_confirm_password(self):
        password = self.cleaned_data.get('password')
        confirm_password = self.cleaned_data.get('confirm_password')
        
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords don't match.")
        
        return confirm_password
    
    def clean_password(self):
        password = self.cleaned_data.get('password')
        
        if not password:
            raise forms.ValidationError("Password is required.")
            
        if len(password) < 8:
            raise forms.ValidationError("Password must be at least 8 characters long.")
        
        if not any(char.isdigit() for char in password):
            raise forms.ValidationError("Password must contain at least one digit.")
        
        if not any(char.isupper() for char in password):
            raise forms.ValidationError("Password must contain at least one uppercase letter.")
        
        return password
from django.contrib.auth.forms import PasswordChangeForm as DjangoPasswordChangeForm

class PasswordChangeForm(DjangoPasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})
from .models import ContactForm

# Contact Form
class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactForm
        fields = ['name', 'email', 'subject', 'message']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your Name',
                'required': True
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your Email',
                'required': True
            }),
            'subject': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Subject',
                'required': True
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Your Message',
                'required': True
            }),
        }