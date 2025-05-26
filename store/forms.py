from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from .models import Review
from .models import Address
from .models import Product
from decimal import Decimal


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'username', 'placeholder': 'Username'}),
        label='Username'
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'id': 'password', 'placeholder': 'Password'}),
        label='Password'
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.error_messages['invalid_login'] = 'Please enter a correct username and password.'
        self.error_messages['inactive'] = 'This account is inactive.'

class RegisterForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'id': 'email', 'placeholder': 'Email'}),
        label='Email'
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control', 'id': 'username', 'placeholder': 'Username'})
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'id': 'password1', 'placeholder': 'Password'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'id': 'password2', 'placeholder': 'Confirm Password'})
        self.fields['username'].help_text = 'Required. 150 characters or fewer. Letters, digits, and @/./+/-/_ only.'
        self.fields['password1'].help_text = 'Your password must contain at least 8 characters.'
        self.fields['password2'].help_text = 'Enter the same password as before, for verification.'

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('This email address is already in use.')
        return email

class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['name', 'locality', 'mobile', 'city', 'state', 'zipcode']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full Name'}),
            'locality': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Street Address'}),
            'mobile': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Mobile Number'}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City'}),
            'state': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'State'}),
            'zipcode': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ZIP Code'}),
        }
        labels = {
            'name': 'Full Name',
            'locality': 'Street Address',
            'mobile': 'Mobile Number',
            'city': 'City',
            'state': 'State',
            'zipcode': 'ZIP Code',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['mobile'].help_text = 'Format: +1234567890 or 1234567890'
        self.fields['zipcode'].help_text = 'Format: 12345 or 12345-6789'

class ContactForm(forms.Form):
    name = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'name', 'placeholder': 'Your Name'}),
        label='Name',
        error_messages={
            'required': 'Please enter your name.',
            'max_length': 'Name cannot exceed 100 characters.'
        }
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'id': 'email', 'placeholder': 'Your Email'}),
        label='Email',
        error_messages={
            'required': 'Please enter your email address.',
            'invalid': 'Please enter a valid email address.'
        }
    )
    message = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={'class': 'form-control', 'id': 'message', 'placeholder': 'Your Message', 'rows': 5}),
        label='Message',
        error_messages={
            'required': 'Please enter a message.'
        }
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['message'].help_text = 'Please provide details of your inquiry.'

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
    
    rating = forms.ChoiceField(choices=[(i, f"{i} sao") for i in range(1, 6)], widget=forms.RadioSelect)
    comment = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Nhập bình luận của bạn...', 'rows': 4}),
        required=False
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['rating'].widget.attrs.update({'class': 'form-control'})
        self.fields['comment'].widget.attrs.update({'class': 'form-control'})

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'

    def clean_price(self):
        price = self.cleaned_data['price']
        if isinstance(price, str):
            price = price.replace('.', '').replace(',', '')
        return Decimal(price)