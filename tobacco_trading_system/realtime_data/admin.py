from django.contrib import admin
from .models import *

@admin.register(RealTimePrice)
class RealTimePriceAdmin(admin.ModelAdmin):
    list_display = ('floor', 'grade', 'current_price', 'previous_price', 'price_change', 'volume_traded_today', 'last_updated')
    list_filter = ('floor', 'grade__category', 'last_updated')
    search_fields = ('floor__name', 'grade__grade_name')
    readonly_fields = ('encrypted_market_data', 'last_updated')

@admin.register(LiveTransaction)
class LiveTransactionAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'floor', 'grade', 'quantity', 'price', 'timestamp', 'is_broadcast')
    list_filter = ('floor', 'grade__category', 'is_broadcast', 'timestamp')
    search_fields = ('transaction_id', 'buyer_info', 'seller_info')
    date_hierarchy = 'timestamp'

@admin.register(MarketAlert)
class MarketAlertAdmin(admin.ModelAdmin):
    list_display = ('alert_type', 'title', 'severity', 'floor', 'grade', 'is_resolved', 'created_at')
    list_filter = ('alert_type', 'severity', 'is_resolved', 'created_at')
    search_fields = ('title', 'message')
    readonly_fields = ('encrypted_alert_data',)
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Alert Information', {
            'fields': ('alert_type', 'title', 'message', 'severity')
        }),
        ('Related Objects', {
            'fields': ('floor', 'grade')
        }),
        ('Status', {
            'fields': ('is_resolved',)
        }),
        ('Alert Data', {
            'fields': ('encrypted_alert_data',),
            'classes': ('collapse',)
        }),
    )

@admin.register(SystemNotification)
class SystemNotificationAdmin(admin.ModelAdmin):
    list_display = ('recipient', 'title', 'notification_type', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read', 'created_at')
    search_fields = ('title', 'message', 'recipient__username')
    readonly_fields = ('encrypted_metadata',)
    date_hierarchy = 'created_at'