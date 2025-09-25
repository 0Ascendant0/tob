from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.utils import timezone
from utils.encryption import encryption
import json
import uuid

class User(AbstractUser):
    """
    Custom User model extending Django's AbstractUser for tobacco trading system
    """
    
    # Override groups and user_permissions to avoid reverse accessor clashes
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        related_name='tobacco_user_set',
        related_query_name='tobacco_user',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='tobacco_user_set',
        related_query_name='tobacco_user',
    )
    
    # Additional user fields
    email = models.EmailField(unique=True, verbose_name='Email Address')
    phone = models.CharField(
        max_length=15, 
        blank=True, 
        null=True,
        verbose_name='Phone Number',
        help_text='Contact phone number'
    )
    
    # Tobacco trading specific fields
    is_timb_staff = models.BooleanField(
        default=False,
        verbose_name='TIMB Staff',
        help_text='Designates whether the user is a TIMB staff member with administrative privileges.'
    )
    is_merchant = models.BooleanField(
        default=False,
        verbose_name='Merchant',
        help_text='Designates whether the user is a registered tobacco merchant.'
    )
    
    # Audit fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        db_table = 'tobacco_auth_user'
    
    def __str__(self):
        return self.username
    
    @property
    def full_name(self):
        """Return the user's full name"""
        return f"{self.first_name} {self.last_name}".strip() or self.username
    
    @property
    def is_tobacco_user(self):
        """Check if user has any tobacco trading permissions"""
        return self.is_timb_staff or self.is_merchant
    
    def get_user_type(self):
        """Return user type as string"""
        if self.is_superuser:
            return 'Super Admin'
        elif self.is_timb_staff:
            return 'TIMB Staff'
        elif self.is_merchant:
            return 'Merchant'
        else:
            return 'Regular User'
    
    def get_theme_preference(self):
        """Get user's theme preference from profile"""
        if hasattr(self, 'profile'):
            return self.profile.theme_preference
        return 'timb'  # Default theme


class UserProfile(models.Model):
    """
    Extended user profile for additional tobacco trading information
    """
    
    THEME_CHOICES = [
        ('timb', 'TIMB Theme'),
        ('merchant', 'Merchant Theme'),
    ]
    
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name='User'
    )
    
    # Company/Business Information
    company_name = models.CharField(
        max_length=200, 
        blank=True, 
        null=True,
        verbose_name='Company Name',
        help_text='Name of the company or business'
    )
    license_number = models.CharField(
        max_length=100, 
        blank=True, 
        null=True,
        verbose_name='License Number',
        help_text='Trading license or registration number'
    )
    registration_date = models.DateField(
        blank=True, 
        null=True,
        verbose_name='Registration Date',
        help_text='Date when the license was issued'
    )
    
    # Contact Information
    address = models.TextField(
        blank=True, 
        null=True,
        verbose_name='Address',
        help_text='Business or contact address'
    )
    website = models.URLField(
        blank=True, 
        null=True,
        verbose_name='Website',
        help_text='Company website URL'
    )
    
    # Preferences
    theme_preference = models.CharField(
        max_length=20,
        choices=THEME_CHOICES,
        default='timb',
        verbose_name='Theme Preference',
        help_text='Preferred dashboard theme'
    )
    
    # Settings
    email_notifications = models.BooleanField(
        default=True,
        verbose_name='Email Notifications',
        help_text='Receive email notifications for important updates'
    )
    sms_notifications = models.BooleanField(
        default=False,
        verbose_name='SMS Notifications',
        help_text='Receive SMS notifications for urgent alerts'
    )
    
    # Encrypted sensitive data storage
    encrypted_sensitive_data = models.TextField(
        blank=True, 
        null=True,
        verbose_name='Encrypted Data',
        help_text='Encrypted storage for sensitive information'
    )
    
    # Metadata
    profile_picture = models.ImageField(
        upload_to='profile_pictures/',
        blank=True,
        null=True,
        verbose_name='Profile Picture'
    )
    bio = models.TextField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name='Bio',
        help_text='Short biography or description'
    )
    
    # Audit fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'
        db_table = 'tobacco_user_profile'
    
    def __str__(self):
        return f"{self.user.username}'s Profile"
    
    def set_sensitive_data(self, data):
        """
        Encrypt and store sensitive user data
        """
        if data:
            try:
                self.encrypted_sensitive_data = encryption.encrypt_data(data)
            except Exception as e:
                print(f"Error encrypting user data: {e}")
                self.encrypted_sensitive_data = None
    
    def get_sensitive_data(self):
        """
        Decrypt and retrieve sensitive user data
        """
        if self.encrypted_sensitive_data:
            try:
                return encryption.decrypt_data(self.encrypted_sensitive_data)
            except Exception as e:
                print(f"Error decrypting user data: {e}")
                return {}
        return {}
    
    def get_display_name(self):
        """Get display name for the user"""
        if self.company_name:
            return self.company_name
        return self.user.full_name
    
    def is_profile_complete(self):
        """Check if user profile is complete"""
        required_fields = ['company_name', 'address']
        if self.user.is_merchant:
            required_fields.append('license_number')
        
        for field in required_fields:
            if not getattr(self, field):
                return False
        return True


class QRToken(models.Model):
    """
    Model for storing QR code tokens in separate database for security
    """
    token = models.CharField(max_length=100, unique=True, db_index=True)
    data_ref = models.CharField(max_length=100, unique=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    access_count = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        app_label = 'qr_tokens'
        db_table = 'qr_tokens'
        verbose_name = 'QR Token'
        verbose_name_plural = 'QR Tokens'
        indexes = [
            models.Index(fields=['token']),
            models.Index(fields=['data_ref']),
            models.Index(fields=['expires_at']),
        ]
    
    def __str__(self):
        return f"QR Token {self.token[:8]}..."
    
    def is_expired(self):
        """Check if the token has expired"""
        return timezone.now() > self.expires_at
    
    def increment_access(self):
        """Increment access count"""
        self.access_count += 1
        self.save(update_fields=['access_count'])


class EncryptedData(models.Model):
    """
    Model for storing encrypted data referenced by QR tokens
    """
    data_ref = models.CharField(max_length=100, unique=True, db_index=True)
    encrypted_content = models.TextField()
    data_type = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Encrypted Data'
        verbose_name_plural = 'Encrypted Data'
        db_table = 'tobacco_encrypted_data'
        indexes = [
            models.Index(fields=['data_ref']),
            models.Index(fields=['data_type']),
        ]
    
    def __str__(self):
        return f"Encrypted Data {self.data_ref[:8]}... ({self.data_type})"
    
    def set_data(self, data, data_type):
        """Encrypt and store data"""
        try:
            self.encrypted_content = encryption.encrypt_data(data)
            self.data_type = data_type
        except Exception as e:
            raise ValueError(f"Failed to encrypt data: {str(e)}")
    
    def get_data(self):
        """Decrypt and return data"""
        try:
            return encryption.decrypt_data(self.encrypted_content)
        except Exception as e:
            raise ValueError(f"Failed to decrypt data: {str(e)}")


class LoginAttempt(models.Model):
    """
    Model to track login attempts for security
    """
    username = models.CharField(max_length=150)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    success = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Login Attempt'
        verbose_name_plural = 'Login Attempts'
        db_table = 'tobacco_login_attempts'
        indexes = [
            models.Index(fields=['username', 'timestamp']),
            models.Index(fields=['ip_address', 'timestamp']),
        ]
    
    def __str__(self):
        status = "Success" if self.success else "Failed"
        return f"{status} login attempt for {self.username} at {self.timestamp}"


class UserSession(models.Model):
    """
    Model to track active user sessions
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    session_key = models.CharField(max_length=40, unique=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'User Session'
        verbose_name_plural = 'User Sessions'
        db_table = 'tobacco_user_sessions'
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['session_key']),
        ]
    
    def __str__(self):
        return f"Session for {self.user.username}"


# Signals to automatically create and save user profiles
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Create a UserProfile when a new User is created
    """
    if created:
        UserProfile.objects.get_or_create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """
    Save the UserProfile when the User is saved
    """
    if hasattr(instance, 'profile'):
        instance.profile.save()
    else:
        # Create profile if it doesn't exist
        UserProfile.objects.get_or_create(user=instance)


@receiver(post_delete, sender=User)
def delete_user_profile(sender, instance, **kwargs):
    """
    Clean up when user is deleted
    """
    # Profile will be deleted automatically due to CASCADE
    pass


# Security-related signals
@receiver(post_save, sender=User)
def log_user_creation(sender, instance, created, **kwargs):
    """
    Log user creation for audit purposes
    """
    if created:
        print(f"New user created: {instance.username} ({instance.get_user_type()})")


# Additional utility functions
def get_user_by_email(email):
    """Get user by email address"""
    try:
        return User.objects.get(email=email)
    except User.DoesNotExist:
        return None


def create_qr_token_for_user(user, data, expiry_minutes=30):
    """Create a QR token for user data"""
    from utils.qr_code import qr_manager
    
    return qr_manager.generate_access_token(data, expiry_minutes)


def validate_user_permissions(user, required_permission):
    """Validate if user has required permissions"""
    if user.is_superuser:
        return True
    
    if required_permission == 'timb_access' and user.is_timb_staff:
        return True
    
    if required_permission == 'merchant_access' and user.is_merchant:
        return True
    
    return False