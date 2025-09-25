from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, UserProfile

class LoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Username or Email',
            'style': 'font-size: 16px;'  # Prevent mobile zoom
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password',
            'style': 'font-size: 16px;'  # Prevent mobile zoom
        })
    )

class RegistrationForm(UserCreationForm):
    USER_TYPES = [
        ('timb', 'TIMB Staff'),
        ('merchant', 'Merchant'),
    ]
    
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'style': 'font-size: 16px;'
        })
    )
    first_name = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'style': 'font-size: 16px;'
        })
    )
    last_name = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'style': 'font-size: 16px;'
        })
    )
    phone = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'style': 'font-size: 16px;'
        })
    )
    user_type = forms.ChoiceField(
        choices=USER_TYPES,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'style': 'font-size: 16px;'
        })
    )
    company_name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'style': 'font-size: 16px;'
        })
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'phone', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'style': 'font-size: 16px;'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'style': 'font-size: 16px;'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'style': 'font-size: 16px;'
        })

class ProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['company_name', 'license_number', 'address', 'theme_preference']
        widgets = {
            'company_name': forms.TextInput(attrs={
                'class': 'form-control',
                'style': 'font-size: 16px;'
            }),
            'license_number': forms.TextInput(attrs={
                'class': 'form-control',
                'style': 'font-size: 16px;'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'style': 'font-size: 16px;'
            }),
            'theme_preference': forms.Select(attrs={
                'class': 'form-control',
                'style': 'font-size: 16px;'
            }),
        }