from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from authentication.models import User, UserProfile


class UserProfileInline(admin.StackedInline):
    """
    Inline admin for UserProfile
    """
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile Information'
    
    fields = (
        'company_name', 
        'license_number', 
        'registration_date',
        'address', 
        'website',
        'theme_preference',
        'email_notifications',
        'sms_notifications',
        'bio'
    )
    
    extra = 0


class UserAdmin(BaseUserAdmin):
    """
    Custom User Admin with tobacco trading specific fields
    """
    
    # Add the profile inline
    inlines = (UserProfileInline,)
    
    # Update list_display to include custom fields
    list_display = (
        'username', 
        'email', 
        'first_name', 
        'last_name', 
        'user_type_display',
        'is_active', 
        'date_joined',
        'profile_status'
    )
    
    # Update list_filter to include custom fields
    list_filter = (
        'is_timb_staff',
        'is_merchant',
        'is_staff', 
        'is_superuser', 
        'is_active', 
        'date_joined',
        'profile__theme_preference'
    )
    
    # Search fields
    search_fields = (
        'username', 
        'first_name', 
        'last_name', 
        'email',
        'profile__company_name',
        'profile__license_number'
    )
    
    # Ordering
    ordering = ('username',)
    
    # Custom fieldsets that include our tobacco trading fields
    fieldsets = (
        (None, {
            'fields': ('username', 'password')
        }),
        ('Personal info', {
            'fields': ('first_name', 'last_name', 'email', 'phone')
        }),
        ('Tobacco Trading Permissions', {
            'fields': ('is_timb_staff', 'is_merchant'),
            'classes': ('wide',),
            'description': 'Grant tobacco trading system specific permissions'
        }),
        ('System Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
            'classes': ('collapse',)
        }),
        ('Important dates', {
            'fields': ('last_login', 'date_joined'),
            'classes': ('collapse',)
        }),
    )
    
    # Fields to show when adding a new user
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2'),
        }),
        ('Personal Information', {
            'classes': ('wide',),
            'fields': ('first_name', 'last_name', 'email', 'phone'),
        }),
        ('Tobacco Trading Permissions', {
            'classes': ('wide',),
            'fields': ('is_timb_staff', 'is_merchant'),
            'description': 'Set tobacco trading system permissions'
        }),
    )
    
    # Custom methods for list display
    def user_type_display(self, obj):
        """Display user type with colored badge"""
        user_type = obj.get_user_type()
        
        if obj.is_superuser:
            color = '#e74c3c'  # Red
            icon = '👑'
        elif obj.is_timb_staff:
            color = '#2E7D32'  # TIMB Green
            icon = '🏛️'
        elif obj.is_merchant:
            color = '#1976D2'  # Merchant Blue
            icon = '🏢'
        else:
            color = '#6c757d'  # Gray
            icon = '👤'
        
        return format_html(
            '<span style="color: {}; font-weight: bold;">{} {}</span>',
            color, icon, user_type
        )
    user_type_display.short_description = 'User Type'
    user_type_display.admin_order_field = 'is_timb_staff'
    
    def profile_status(self, obj):
        """Display profile completion status"""
        if hasattr(obj, 'profile'):
            if obj.profile.is_profile_complete():
                return format_html(
                    '<span style="color: green; font-weight: bold;">✓ Complete</span>'
                )
            else:
                return format_html(
                    '<span style="color: orange; font-weight: bold;">⚠ Incomplete</span>'
                )
        else:
            return format_html(
                '<span style="color: red; font-weight: bold;">✗ Missing</span>'
            )
    profile_status.short_description = 'Profile'
    
    # Custom actions
    actions = ['activate_users', 'deactivate_users', 'make_timb_staff', 'make_merchant']
    
    def activate_users(self, request, queryset):
        """Activate selected users"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} user(s) were successfully activated.')
    activate_users.short_description = 'Activate selected users'
    
    def deactivate_users(self, request, queryset):
        """Deactivate selected users"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} user(s) were successfully deactivated.')
    deactivate_users.short_description = 'Deactivate selected users'
    
    def make_timb_staff(self, request, queryset):
        """Make selected users TIMB staff"""
        updated = queryset.update(is_timb_staff=True, is_merchant=False)
        self.message_user(request, f'{updated} user(s) were made TIMB staff.')
    make_timb_staff.short_description = 'Make selected users TIMB staff'
    
    def make_merchant(self, request, queryset):
        """Make selected users merchants"""
        updated = queryset.update(is_merchant=True, is_timb_staff=False)
        self.message_user(request, f'{updated} user(s) were made merchants.')
    make_merchant.short_description = 'Make selected users merchants'


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """
    Admin interface for UserProfile model
    """
    
    list_display = (
        'user_display',
        'company_name', 
        'license_number',
        'theme_preference',
        'profile_complete',
        'created_at'
    )
    
    list_filter = (
        'theme_preference',
        'email_notifications',
        'sms_notifications',
        'created_at',
        'user__is_timb_staff',
        'user__is_merchant'
    )
    
    search_fields = (
        'user__username', 
        'user__first_name',
        'user__last_name',
        'company_name', 
        'license_number',
        'address'
    )
    
    readonly_fields = ('created_at', 'updated_at', 'encrypted_sensitive_data')
    
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Company Details', {
            'fields': (
                'company_name', 
                'license_number', 
                'registration_date',
                'address', 
                'website'
            )
        }),
        ('Preferences', {
            'fields': (
                'theme_preference',
                'email_notifications',
                'sms_notifications'
            )
        }),
        ('Additional Information', {
            'fields': ('bio', 'profile_picture'),
            'classes': ('collapse',)
        }),
        ('System Information', {
            'fields': ('encrypted_sensitive_data', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    # Custom methods
    def user_display(self, obj):
        """Display user with link to user admin"""
        return format_html(
            '<a href="{}">{}</a>',
            reverse('admin:authentication_user_change', args=[obj.user.pk]),
            obj.user.username
        )
    user_display.short_description = 'User'
    user_display.admin_order_field = 'user__username'
    
    def profile_complete(self, obj):
        """Display profile completion status"""
        if obj.is_profile_complete():
            return format_html(
                '<span style="color: green; font-weight: bold;">✓ Complete</span>'
            )
        else:
            return format_html(
                '<span style="color: orange; font-weight: bold;">⚠ Incomplete</span>'
            )
    profile_complete.short_description = 'Status'
    profile_complete.boolean = True


# Unregister the default User admin if it exists
try:
    admin.site.unregister(User)
except admin.sites.NotRegistered:
    pass

# Register our custom User admin
admin.site.register(User, UserAdmin)

# Customize admin site header and title
admin.site.site_header = "TIMB Trading System Administration"
admin.site.site_title = "TIMB Admin"
admin.site.index_title = "Welcome to TIMB Trading System Administration"