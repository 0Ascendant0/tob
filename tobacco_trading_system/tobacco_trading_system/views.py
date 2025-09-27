from django.shortcuts import render, redirect
from django.http import HttpResponseNotFound, HttpResponseServerError

def handler404(request, exception):
    """Custom 404 error page"""
    context = {
        'error_message': 'The page you are looking for does not exist.',
        'error_code': '404'
    }
    return render(request, '404.html', context, status=404)

def handler500(request):
    """Custom 500 error page"""
    context = {
        'error_message': 'An internal server error occurred.',
        'error_code': '500'
    }
    return render(request, '500.html', context, status=500)

def home(request):
    """Home page view"""
    if request.user.is_authenticated:
        if hasattr(request.user, 'is_timb_staff') and request.user.is_timb_staff:
            return redirect('timb_dashboard:dashboard')
        elif hasattr(request.user, 'is_merchant') and request.user.is_merchant:
            return redirect('merchant_dashboard')
    return redirect('login')