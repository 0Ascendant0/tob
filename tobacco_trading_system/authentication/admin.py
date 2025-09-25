from django.contrib import admin
from .models import User, UserProfile

# Note: The main admin configuration for User and UserProfile 
# is handled in timb_dashboard/admin.py to avoid conflicts.
# 
# If you need basic admin functionality here, you can uncomment
# the code below, but make sure to remove the registration
# from timb_dashboard/admin.py first.

# Uncomment below if you want to register UserProfile here instead
# of in timb_dashboard/admin.py

# @admin.register(UserProfile)
# class UserProfileSimpleAdmin(admin.ModelAdmin):
#     """
#     Simple UserProfile admin for authentication app
#     """
#     
#     list_display = (
#         'user', 
#         'company_name', 
#         'license_number', 
#         'theme_preference'
#     )
#     
#     list_filter = (
#         'theme_preference',
#         'created_at'
#     )
#     
#     search_fields = (
#         'user__username',
#         'company_name',
#         'license_number'
#     )
#     
#     readonly_fields = ('created_at', 'updated_at')
#     
#     fields = (
#         'user',
#         'company_name',
#         'license_number',
#         'registration_date',
#         'address',
#         'website',
#         'theme_preference',
#         'email_notifications',
#         'sms_notifications',
#         'bio',
#         'created_at',
#         'updated_at'
#     )


# Note: User admin is handled in timb_dashboard/admin.py
# The custom User model with tobacco trading fields is registered there
# to provide comprehensive admin functionality.

# If you prefer to have basic User admin here, uncomment below:
# from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
# 
# class AuthUserAdmin(BaseUserAdmin):
#     """Basic User admin for authentication app"""
#     
#     list_display = (
#         'username', 
#         'email', 
#         'first_name', 
#         'last_name', 
#         'is_timb_staff',
#         'is_merchant',
#         'is_active'
#     )
#     
#     list_filter = (
#         'is_timb_staff',
#         'is_merchant',
#         'is_active',
#         'date_joined'
#     )
#     
#     fieldsets = BaseUserAdmin.fieldsets + (
#         ('Tobacco Trading', {
#             'fields': ('is_timb_staff', 'is_merchant', 'phone')
#         }),
#     )
#     
#     add_fieldsets = BaseUserAdmin.add_fieldsets + (
#         ('Additional Info', {
#             'fields': ('email', 'first_name', 'last_name', 'phone', 'is_timb_staff', 'is_merchant')
#         }),
#     )
# 
# # Only register if not already registered in timb_dashboard
# try:
#     admin.site.register(User, AuthUserAdmin)
# except admin.sites.AlreadyRegistered:
#     pass