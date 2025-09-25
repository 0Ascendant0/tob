from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from .models import User, UserProfile
from .forms import LoginForm, RegistrationForm, ProfileForm
import json

class LoginView(View):
    def get(self, request):
        if request.user.is_authenticated:
            # Check the User model fields, not profile fields
            if request.user.is_merchant:
                return redirect('merchant_dashboard')
            else:
                return redirect('timb_dashboard')
        
        form = LoginForm()
        return render(request, 'authentication/login.html', {'form': form})
    
    def post(self, request):
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            
            if user:
                login(request, user)
                # Check the User model fields, not profile fields
                if user.is_merchant:
                    return redirect('merchant_dashboard')
                else:
                    return redirect('timb_dashboard')
            else:
                messages.error(request, 'Invalid credentials')
        
        return render(request, 'authentication/login.html', {'form': form})

class RegisterView(View):
    def get(self, request):
        form = RegistrationForm()
        return render(request, 'authentication/register.html', {'form': form})
    
    def post(self, request):
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            
            # Set user type fields on the User model
            user_type = form.cleaned_data.get('user_type')
            if user_type == 'merchant':
                user.is_merchant = True
                user.is_timb_staff = False
            else:  # timb
                user.is_timb_staff = True
                user.is_merchant = False
            
            user.save()
            
            # Update the automatically created profile
            profile, created = UserProfile.objects.get_or_create(
                user=user,
                defaults={
                    'company_name': form.cleaned_data.get('company_name', ''),
                }
            )
            
            if not created:
                profile.company_name = form.cleaned_data.get('company_name', '')
                profile.save()
            
            messages.success(request, 'Account created successfully')
            return redirect('login')
        
        return render(request, 'authentication/register.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    messages.success(request, 'Logged out successfully')
    return redirect('login')

@login_required
def profile_view(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully')
            return redirect('profile')
    else:
        form = ProfileForm(instance=profile)
    
    return render(request, 'authentication/profile.html', {'form': form})