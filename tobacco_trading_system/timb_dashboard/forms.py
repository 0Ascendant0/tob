from django import forms
from django.contrib.auth import get_user_model
User = get_user_model()
from .models import Transaction, TobaccoGrade, TobaccoFloor, DailyPrice, SystemAlert, Merchant


class TransactionForm(forms.ModelForm):
    """Form for recording tobacco transactions"""
    
    class Meta:
        model = Transaction
        fields = [
            'transaction_type', 'seller', 'buyer', 'grade', 'quantity',
            'price_per_kg', 'floor', 'payment_method', 'moisture_content',
            'quality_assessment', 'sale_number', 'lot_number'
        ]
        widgets = {
            'transaction_type': forms.Select(attrs={'class': 'form-control'}),
            'seller': forms.Select(attrs={'class': 'form-control'}),
            'buyer': forms.Select(attrs={'class': 'form-control'}),
            'grade': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'price_per_kg': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'floor': forms.Select(attrs={'class': 'form-control'}),
            'payment_method': forms.Select(attrs={'class': 'form-control'}),
            'moisture_content': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'quality_assessment': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'sale_number': forms.TextInput(attrs={'class': 'form-control'}),
            'lot_number': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Filter merchants for seller and buyer
        merchants = User.objects.filter(groups__name='Merchants').order_by('username')
        self.fields['seller'].queryset = merchants
        self.fields['buyer'].queryset = merchants
        
        # Filter active grades
        self.fields['grade'].queryset = TobaccoGrade.objects.filter(
            is_active=True, is_tradeable=True
        ).order_by('grade_code')
        
        # Filter active floors
        self.fields['floor'].queryset = TobaccoFloor.objects.filter(
            is_active=True
        ).order_by('name')


class PriceFilterForm(forms.Form):
    """Form for filtering price data"""
    grade = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Grade code...'
        })
    )
    floor = forms.ModelChoiceField(
        queryset=TobaccoFloor.objects.filter(is_active=True),
        required=False,
        empty_label="All Floors",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )


class GradeManagementForm(forms.ModelForm):
    """Form for managing tobacco grades"""
    
    class Meta:
        model = TobaccoGrade
        fields = [
            'grade_code', 'grade_name', 'category', 'quality_level',
            'base_price', 'minimum_price', 'maximum_price',
            'description', 'is_active', 'is_tradeable'
        ]
        widgets = {
            'grade_code': forms.TextInput(attrs={'class': 'form-control'}),
            'grade_name': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'quality_level': forms.Select(attrs={'class': 'form-control'}),
            'base_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'minimum_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'maximum_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_tradeable': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class FloorManagementForm(forms.ModelForm):
    """Form for managing tobacco floors"""
    
    class Meta:
        model = TobaccoFloor
        fields = [
            'name', 'location', 'address', 'manager', 'phone', 'email',
            'capacity', 'is_active'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'manager': forms.Select(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'capacity': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Filter TIMB staff for manager field
        self.fields['manager'].queryset = User.objects.filter(
            is_staff=True
        ).order_by('username')


class MerchantCreationForm(forms.ModelForm):
    """Form for creating new merchants from TIMB dashboard"""

    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Username for login'
        }),
        help_text='Username for merchant login'
    )

    # Email no longer required/used on the create merchant page
    email = forms.EmailField(required=False, widget=forms.HiddenInput())

    first_name = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'First name'
        })
    )

    last_name = forms.CharField(
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Last name'
        })
    )

    # Phone removed from the create merchant page UI
    phone = forms.CharField(max_length=20, required=False, widget=forms.HiddenInput())

    class Meta:
        model = Merchant
        fields = [
            'company_name', 'license_number', 'business_address',
            'business_phone', 'business_email'
        ]
        widgets = {
            'company_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Company name'
            }),
            'license_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'License number'
            }),
            'business_address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Business address'
            }),
            'business_phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Business phone'
            }),
            'business_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Business email'
            }),
            # Banking fields removed
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make license_number required
        self.fields['license_number'].required = True
        self.fields['company_name'].required = True

    def clean_license_number(self):
        license_number = self.cleaned_data.get('license_number')
        if Merchant.objects.filter(license_number=license_number).exists():
            raise forms.ValidationError('A merchant with this license number already exists.')
        return license_number

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('This username is already taken.')
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('A user with this email already exists.')
        return email


class AlertResolutionForm(forms.ModelForm):
    """Form for resolving system alerts"""

    resolution_notes = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Resolution notes...'
        }),
        required=False
    )

    class Meta:
        model = SystemAlert
        fields = ['resolution_notes']