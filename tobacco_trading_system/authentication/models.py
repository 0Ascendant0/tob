from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from utils.encryption import encryption
import json


class User(AbstractUser):
    """Enhanced custom user model for TIMB system"""
    
    # Additional user types
    is_timb_staff = models.BooleanField(default=False, help_text='TIMB staff member')
    is_merchant = models.BooleanField(default=False, help_text='Tobacco merchant')
    
    # Enhanced user information
    phone = models.CharField(max_length=20, blank=True)
    national_id = models.CharField(max_length=50, blank=True)
    
    # Account status
    is_verified = models.BooleanField(default=False)
    verification_token = models.CharField(max_length=100, blank=True)
    verification_sent_at = models.DateTimeField(blank=True, null=True)
    
    # Security settings
    two_factor_enabled = models.BooleanField(default=False)
    backup_codes = models.JSONField(default=list, blank=True)
    login_attempts = models.IntegerField(default=0)
    locked_until = models.DateTimeField(blank=True, null=True)
    
    # Login tracking
    last_login_ip = models.GenericIPAddressField(blank=True, null=True)
    last_login_device = models.CharField(max_length=200, blank=True)
    login_history = models.JSONField(default=list, blank=True)
    
    # Password management
    password_changed_at = models.DateTimeField(auto_now_add=True)
    password_reset_required = models.BooleanField(default=False)
    
    # Notification preferences
    email_notifications = models.BooleanField(default=True)
    sms_notifications = models.BooleanField(default=False)
    push_notifications = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def __str__(self):
        return f"{self.username} ({self.get_user_type()})"
    
    def get_user_type(self):
        """Get user type for display"""
        if self.is_superuser:
            return "Administrator"
        elif self.is_timb_staff:
            return "TIMB Staff"
        elif self.is_merchant:
            return "Merchant"
        else:
            return "User"
    
    def can_login(self):
        """Check if user can login (not locked)"""
        if self.locked_until:
            return timezone.now() > self.locked_until
        return True
    
    def lock_account(self, duration_minutes=30):
        """Lock account for specified duration"""
        self.locked_until = timezone.now() + timezone.timedelta(minutes=duration_minutes)
        self.save()
    
    def unlock_account(self):
        """Unlock account"""
        self.locked_until = None
        self.login_attempts = 0
        self.save()
    
    def record_login_attempt(self, success=False, ip_address=None, device_info=''):
        """Record login attempt"""
        if success:
            self.login_attempts = 0
            self.last_login_ip = ip_address
            self.last_login_device = device_info
            
            # Add to login history (keep last 10)
            login_record = {
                'timestamp': timezone.now().isoformat(),
                'ip': ip_address,
                'device': device_info,
                'success': True
            }
            
            self.login_history.append(login_record)
            if len(self.login_history) > 10:
                self.login_history = self.login_history[-10:]
        else:
            self.login_attempts += 1
            if self.login_attempts >= 5:
                self.lock_account()
        
        self.save()


class UserProfile(models.Model):
    """Enhanced user profile with business information"""
    
    THEME_CHOICES = [
        ('timb', 'TIMB Theme'),
        ('merchant', 'Merchant Theme'),
        ('light', 'Light Theme'),
        ('dark', 'Dark Theme'),
        ('custom', 'Custom Theme'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    # Business Information
    company_name = models.CharField(max_length=200, blank=True)
    license_number = models.CharField(max_length=100, blank=True)
    registration_date = models.DateField(blank=True, null=True)
    business_address = models.TextField(blank=True)
    
    # Contact Information
    address = models.TextField(blank=True)
    website = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)
    
    # Profile customization
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    bio = models.TextField(max_length=500, blank=True)
    theme_preference = models.CharField(max_length=20, choices=THEME_CHOICES, default='timb')
    
    # Notification preferences
    email_notifications = models.BooleanField(default=True)
    sms_notifications = models.BooleanField(default=False)
    
    # Dashboard preferences
    dashboard_layout = models.JSONField(default=dict, blank=True)
    widget_preferences = models.JSONField(default=dict, blank=True)
    
    # Privacy settings
    profile_visibility = models.CharField(max_length=20, choices=[
        ('PUBLIC', 'Public'),
        ('MERCHANTS_ONLY', 'Merchants Only'),
        ('PRIVATE', 'Private'),
    ], default='MERCHANTS_ONLY')
    
    show_activity_status = models.BooleanField(default=True)
    allow_contact = models.BooleanField(default=True)
    
    # Encrypted sensitive data
    encrypted_sensitive_data = models.TextField(blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'
    
    def __str__(self):
        return f"{self.user.username} - Profile"
    
    def set_sensitive_data(self, data):
        """Encrypt and store sensitive data"""
        if data:
            self.encrypted_sensitive_data = encryption.encrypt_data(data)
    
    def get_sensitive_data(self):
        """Decrypt and retrieve sensitive data"""
        if self.encrypted_sensitive_data:
            return encryption.decrypt_data(self.encrypted_sensitive_data)
        return {}
    
    def is_profile_complete(self):
        """Check if profile is complete"""
        required_fields = ['company_name'] if self.user.is_merchant else []
        
        for field in required_fields:
            if not getattr(self, field):
                return False
        
        return True


class QRToken(models.Model):
    """Secure QR code tokens for data access"""
    
    token = models.CharField(max_length=100, unique=True)
    data_ref = models.CharField(max_length=100)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    
    # Token metadata
    token_type = models.CharField(max_length=50, default='data_access')
    description = models.CharField(max_length=200, blank=True)
    
    # Access control
    access_count = models.IntegerField(default=0)
    max_uses = models.IntegerField(default=10)
    expires_at = models.DateTimeField()
    
    # Security
    is_revoked = models.BooleanField(default=False)
    revoked_at = models.DateTimeField(blank=True, null=True)
    revoked_by = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name='revoked_tokens')
    
    # Audit
    created_at = models.DateTimeField(auto_now_add=True)
    last_accessed = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        verbose_name = 'QR Token'
        verbose_name_plural = 'QR Tokens'
        indexes = [
            models.Index(fields=['token']),
            models.Index(fields=['expires_at']),
        ]
    
    def __str__(self):
        return f"QR Token {self.token[:8]}... ({self.token_type})"
    
    def is_valid(self):
        """Check if token is still valid"""
        if self.is_revoked:
            return False
        if timezone.now() > self.expires_at:
            return False
        if self.access_count >= self.max_uses:
            return False
        return True
    
    def use_token(self):
        """Use the token (increment access count)"""
        if self.is_valid():
            self.access_count += 1
            self.last_accessed = timezone.now()
            self.save()
            return True
        return False
    
    def revoke(self, revoked_by=None):
        """Revoke the token"""
        self.is_revoked = True
        self.revoked_at = timezone.now()
        self.revoked_by = revoked_by
        self.save()


class EncryptedData(models.Model):
    """Secure storage for encrypted data referenced by QR tokens"""
    
    data_ref = models.CharField(max_length=100, unique=True, db_index=True)
    encrypted_content = models.TextField()
    content_type = models.CharField(max_length=50)
    
    # Access control
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    access_permissions = models.JSONField(default=dict, blank=True)
    
    # Lifecycle
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        verbose_name = 'Encrypted Data'
        verbose_name_plural = 'Encrypted Data'
        db_table = 'qr_tokens_encrypteddata'
    
    def __str__(self):
        return f"Encrypted Data {self.data_ref} ({self.content_type})"
    
    def get_content(self):
        """Decrypt and return content"""
        return encryption.decrypt_data(self.encrypted_content)
    
    def set_content(self, content):
        """Encrypt and store content"""
        self.encrypted_content = encryption.encrypt_data(content)
    
    def is_expired(self):
        """Check if data has expired"""
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False


class UserSession(models.Model):
    """Enhanced user session tracking"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_sessions')
    session_key = models.CharField(max_length=40, unique=True)
    
    # Session details
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    device_type = models.CharField(max_length=50, blank=True)
    browser_info = models.CharField(max_length=200, blank=True)
    
    # Location (if available)
    country = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)
    
    # Session status
    is_active = models.BooleanField(default=True)
    login_time = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)
    logout_time = models.DateTimeField(blank=True, null=True)
    
    # Security flags
    is_suspicious = models.BooleanField(default=False)
    security_score = models.DecimalField(max_digits=5, decimal_places=2, default=100.00)
    
    class Meta:
        verbose_name = 'User Session'
        verbose_name_plural = 'User Sessions'
        ordering = ['-last_activity']
    
    def __str__(self):
        return f"{self.user.username} - {self.ip_address} ({self.login_time})"
    
    def end_session(self):
        """End the session"""
        self.is_active = False
        self.logout_time = timezone.now()
        self.save()
    
    @property
    def duration(self):
        """Calculate session duration"""
        end_time = self.logout_time or timezone.now()
        return end_time - self.login_time


class SecurityLog(models.Model):
    """Security event logging"""
    
    EVENT_TYPES = [
        ('LOGIN_SUCCESS', 'Successful Login'),
        ('LOGIN_FAILED', 'Failed Login'),
        ('LOGOUT', 'Logout'),
        ('PASSWORD_CHANGE', 'Password Change'),
        ('PROFILE_UPDATE', 'Profile Update'),
        ('SUSPICIOUS_ACTIVITY', 'Suspicious Activity'),
        ('ACCOUNT_LOCKED', 'Account Locked'),
        ('ACCOUNT_UNLOCKED', 'Account Unlocked'),
        ('TOKEN_GENERATED', 'Token Generated'),
        ('TOKEN_USED', 'Token Used'),
        ('DATA_ACCESS', 'Data Access'),
        ('PERMISSION_CHANGE', 'Permission Change'),
    ]
    
    SEVERITY_LEVELS = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('CRITICAL', 'Critical'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    event_type = models.CharField(max_length=30, choices=EVENT_TYPES)
    severity = models.CharField(max_length=10, choices=SEVERITY_LEVELS, default='LOW')
    
    # Event details
    description = models.TextField()
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True)
    
    # Additional context
    additional_data = models.JSONField(default=dict, blank=True)
    
    # Timestamps
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Security Log'
        verbose_name_plural = 'Security Logs'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['event_type', 'timestamp']),
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['severity', 'timestamp']),
        ]
    
    def __str__(self):
        return f"{self.get_event_type_display()} - {self.user.username if self.user else 'Anonymous'}"


# Signal handlers to create profiles automatically
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create user profile when user is created"""
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Save user profile when user is saved"""
    if hasattr(instance, 'profile'):
        instance.profile.save()