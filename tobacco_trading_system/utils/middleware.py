from django.utils import timezone
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.contrib import messages
from django.http import JsonResponse
import json

class SecurityMiddleware:
    """Enhanced security middleware for session management"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Pre-process request
        if request.user.is_authenticated:
            self.check_session_security(request)
            self.update_last_activity(request)
        
        response = self.get_response(request)
        
        # Post-process response
        return response
    
    def check_session_security(self, request):
        """Check session security and validity"""
        user = request.user
        
        # Check if account is locked
        if hasattr(user, 'locked_until') and user.locked_until:
            if timezone.now() < user.locked_until:
                logout(request)
                messages.error(request, 'Your account is temporarily locked.')
                return redirect('login')
        
        # Check password reset requirement
        if hasattr(user, 'password_reset_required') and user.password_reset_required:
            if request.path not in ['/auth/change-password/', '/auth/logout/']:
                messages.warning(request, 'You must change your password.')
                return redirect('change_password')
    
    def update_last_activity(self, request):
        """Update user session last activity"""
        try:
            from authentication.models import UserSession
            
            session = UserSession.objects.filter(
                user=request.user,
                session_key=request.session.session_key,
                is_active=True
            ).first()
            
            if session:
                session.last_activity = timezone.now()
                session.save()
        except:
            pass  # Fail silently


class AuditMiddleware:
    """Audit middleware for tracking user actions"""
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.sensitive_paths = [
            '/admin/',
            '/api/',
            '/timb/',
            '/merchant/',
            '/auth/profile/',
        ]
    
    def __call__(self, request):
        # Log request if on sensitive path
        if any(request.path.startswith(path) for path in self.sensitive_paths):
            self.log_request(request)
        
        response = self.get_response(request)
        return response
    
    def log_request(self, request):
        """Log user request for audit purposes"""
        try:
            from authentication.models import SecurityLog
            
            if request.user.is_authenticated:
                SecurityLog.objects.create(
                    user=request.user,
                    event_type='PAGE_ACCESS',
                    severity='LOW',
                    description=f'Accessed: {request.path}',
                    ip_address=self.get_client_ip(request),
                    user_agent=request.META.get('HTTP_USER_AGENT', ''),
                    additional_data={
                        'method': request.method,
                        'path': request.path,
                        'query_params': dict(request.GET)
                    }
                )
        except:
            pass  # Fail silently
    
    def get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class RealTimeUpdateMiddleware:
    """Middleware for real-time data updates"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)
        
        # Add real-time headers
        if request.path.startswith('/api/'):
            response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response['Pragma'] = 'no-cache'
            response['Expires'] = '0'
        
        return response


class ThemeMiddleware:
    """Middleware for handling user theme preferences"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Set theme context
        if request.user.is_authenticated:
            try:
                from authentication.models import UserProfile
                profile = UserProfile.objects.get(user=request.user)
                request.theme = profile.theme_preference
            except:
                request.theme = 'timb'  # Default theme
        else:
            request.theme = 'timb'
        
        response = self.get_response(request)
        return response