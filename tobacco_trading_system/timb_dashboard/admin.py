from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.db.models import Count, Sum, Avg
from django.utils import timezone
from datetime import timedelta
import json

from .models import (
    TobaccoGrade, TobaccoFloor, Transaction, DailyPrice, 
    DashboardMetric, SystemAlert, UserSession
)


@admin.register(TobaccoGrade)
class TobaccoGradeAdmin(admin.ModelAdmin):
    list_display = [
        'grade_code', 'grade_name', 'category', 'quality_level', 
        'base_price', 'is_active', 'is_tradeable', 'transaction_count'
    ]
    list_filter = ['category', 'quality_level', 'is_active', 'is_tradeable']
    search_fields = ['grade_code', 'grade_name']
    readonly_fields = ['created_at', 'updated_at', 'transaction_stats']
    ordering = ['category', 'quality_level', 'grade_code']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('grade_code', 'grade_name', 'category', 'quality_level', 'description')
        }),
        ('Pricing', {
            'fields': ('base_price', 'minimum_price', 'maximum_price')
        }),
        ('Status', {
            'fields': ('is_active', 'is_tradeable')
        }),
        ('Technical Details', {
            'fields': ('specifications',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
        ('Statistics', {
            'fields': ('transaction_stats',),
            'classes': ('collapse',)
        })
    )
    
    def transaction_count(self, obj):
        return obj.transaction_set.count()
    transaction_count.short_description = 'Transactions'
    
    def transaction_stats(self, obj):
        transactions = obj.transaction_set.all()
        if transactions.exists():
            stats = transactions.aggregate(
                total_volume=Sum('quantity'),
                avg_price=Avg('price_per_kg'),
                total_value=Sum('total_amount')
            )
            return format_html(
                '<div style="background: #f8f9fa; padding: 10px; border-radius: 4px;">'
                '<strong>Total Volume:</strong> {:.2f} kg<br>'
                '<strong>Average Price:</strong> ${:.2f}/kg<br>'
                '<strong>Total Value:</strong> ${:.2f}<br>'
                '<strong>Transaction Count:</strong> {}'
                '</div>',
                stats['total_volume'] or 0,
                stats['avg_price'] or 0,
                stats['total_value'] or 0,
                transactions.count()
            )
        return "No transactions recorded"
    transaction_stats.short_description = 'Transaction Statistics'
    
    actions = ['activate_grades', 'deactivate_grades', 'make_tradeable', 'make_non_tradeable']
    
    def activate_grades(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} grades activated.')
    activate_grades.short_description = 'Activate selected grades'
    
    def deactivate_grades(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} grades deactivated.')
    deactivate_grades.short_description = 'Deactivate selected grades'
    
    def make_tradeable(self, request, queryset):
        updated = queryset.update(is_tradeable=True)
        self.message_user(request, f'{updated} grades made tradeable.')
    make_tradeable.short_description = 'Make selected grades tradeable'
    
    def make_non_tradeable(self, request, queryset):
        updated = queryset.update(is_tradeable=False)
        self.message_user(request, f'{updated} grades made non-tradeable.')
    make_non_tradeable.short_description = 'Make selected grades non-tradeable'


@admin.register(TobaccoFloor)
class TobaccoFloorAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'location', 'manager', 'capacity', 'current_stock', 
        'utilization_display', 'is_active', 'transaction_count'
    ]
    list_filter = ['is_active', 'location']
    search_fields = ['name', 'location', 'manager__username']
    readonly_fields = ['created_at', 'utilization_percentage', 'floor_statistics']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'location', 'address', 'manager')
        }),
        ('Contact Information', {
            'fields': ('phone', 'email')
        }),
        ('Capacity & Status', {
            'fields': ('capacity', 'current_stock', 'utilization_percentage', 'is_active')
        }),
        ('Operational Details', {
            'fields': ('operating_hours', 'coordinates'),
            'classes': ('collapse',)
        }),
        ('Statistics', {
            'fields': ('floor_statistics',),
            'classes': ('collapse',)
        })
    )
    
    def utilization_display(self, obj):
        percentage = obj.utilization_percentage
        if percentage > 90:
            color = 'red'
        elif percentage > 70:
            color = 'orange'
        else:
            color = 'green'
        
        return format_html(
            '<span style="color: {}; font-weight: bold;">{:.1f}%</span>',
            color, percentage
        )
    utilization_display.short_description = 'Utilization'
    
    def transaction_count(self, obj):
        return obj.transaction_set.count()
    transaction_count.short_description = 'Transactions'
    
    def floor_statistics(self, obj):
        transactions = obj.transaction_set.all()
        if transactions.exists():
            today = timezone.now().date()
            week_ago = today - timedelta(days=7)
            
            recent_transactions = transactions.filter(timestamp__date__gte=week_ago)
            
            stats = transactions.aggregate(
                total_volume=Sum('quantity'),
                total_value=Sum('total_amount'),
                avg_price=Avg('price_per_kg')
            )
            
            recent_stats = recent_transactions.aggregate(
                recent_volume=Sum('quantity'),
                recent_transactions=Count('id')
            )
            
            return format_html(
                '<div style="background: #f8f9fa; padding: 10px; border-radius: 4px;">'
                '<h4>All Time Statistics:</h4>'
                '<strong>Total Volume:</strong> {:.2f} kg<br>'
                '<strong>Total Value:</strong> ${:.2f}<br>'
                '<strong>Average Price:</strong> ${:.2f}/kg<br>'
                '<strong>Total Transactions:</strong> {}<br><br>'
                '<h4>Last 7 Days:</h4>'
                '<strong>Volume:</strong> {:.2f} kg<br>'
                '<strong>Transactions:</strong> {}'
                '</div>',
                stats['total_volume'] or 0,
                stats['total_value'] or 0,
                stats['avg_price'] or 0,
                transactions.count(),
                recent_stats['recent_volume'] or 0,
                recent_stats['recent_transactions'] or 0
            )
        return "No transactions recorded"
    floor_statistics.short_description = 'Floor Statistics'


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = [
        'transaction_id', 'transaction_type', 'seller', 'buyer', 
        'grade', 'quantity', 'price_per_kg', 'total_amount', 
        'status', 'is_flagged', 'timestamp'
    ]
    list_filter = [
        'transaction_type', 'status', 'is_flagged', 'grade__category',
        'floor', 'timestamp', 'payment_method'
    ]
    search_fields = [
        'transaction_id', 'seller__username', 'buyer__username', 
        'grade__grade_code', 'sale_number', 'lot_number'
    ]
    readonly_fields = [
        'transaction_id', 'total_amount', 'timestamp', 'updated_at',
        'fraud_analysis', 'price_analysis'
    ]
    date_hierarchy = 'timestamp'
    ordering = ['-timestamp']
    
    fieldsets = (
        ('Transaction Details', {
            'fields': ('transaction_id', 'transaction_type', 'status')
        }),
        ('Parties', {
            'fields': ('seller', 'buyer')
        }),
        ('Product Information', {
            'fields': ('grade', 'quantity', 'price_per_kg', 'total_amount')
        }),
        ('Location & Sale Details', {
            'fields': ('floor', 'sale_number', 'lot_number')
        }),
        ('Quality Information', {
            'fields': ('moisture_content', 'quality_assessment', 'quality_score'),
            'classes': ('collapse',)
        }),
        ('Payment Information', {
            'fields': ('payment_method', 'payment_reference', 'payment_date'),
            'classes': ('collapse',)
        }),
        ('Fraud Detection', {
            'fields': ('is_flagged', 'fraud_score', 'fraud_reasons', 'fraud_analysis'),
            'classes': ('collapse',)
        }),
        ('Analysis', {
            'fields': ('price_analysis',),
            'classes': ('collapse',)
        }),
        ('System Information', {
            'fields': ('created_by', 'timestamp', 'updated_at', 'metadata'),
            'classes': ('collapse',)
        })
    )
    
    def fraud_analysis(self, obj):
        if obj.is_flagged:
            return format_html(
                '<div style="background: #ffebee; padding: 10px; border: 1px solid #f44336; border-radius: 4px;">'
                '<h4 style="color: #d32f2f; margin-top: 0;">⚠️ FRAUD ALERT</h4>'
                '<strong>Fraud Score:</strong> {:.2%}<br>'
                '<strong>Reasons:</strong><br>'
                '<ul style="margin: 5px 0;">{}</ul>'
                '</div>',
                obj.fraud_score,
                ''.join([f'<li>{reason}</li>' for reason in obj.fraud_reasons])
            )
        else:
            return format_html(
                '<div style="background: #e8f5e8; padding: 10px; border: 1px solid #4caf50; border-radius: 4px;">'
                '<h4 style="color: #2e7d32; margin-top: 0;">✅ CLEAN TRANSACTION</h4>'
                'No fraud indicators detected'
                '</div>'
            )
    fraud_analysis.short_description = 'Fraud Analysis'
    
    def price_analysis(self, obj):
        if obj.grade.base_price > 0:
            deviation = ((obj.price_per_kg - obj.grade.base_price) / obj.grade.base_price) * 100
            
            if abs(deviation) > 20:
                color = '#f44336'
                status = '⚠️ SIGNIFICANT DEVIATION'
            elif abs(deviation) > 10:
                color = '#ff9800'
                status = '⚡ MODERATE DEVIATION'
            else:
                color = '#4caf50'
                status = '✅ NORMAL RANGE'
            
            return format_html(
                '<div style="background: #f8f9fa; padding: 10px; border-left: 4px solid {}; border-radius: 4px;">'
                '<h4 style="color: {}; margin-top: 0;">{}</h4>'
                '<strong>Transaction Price:</strong> ${:.2f}/kg<br>'
                '<strong>Base Price:</strong> ${:.2f}/kg<br>'
                '<strong>Deviation:</strong> {:+.1f}%<br>'
                '<strong>Price Range:</strong> ${:.2f} - ${:.2f}/kg'
                '</div>',
                color, color, status,
                obj.price_per_kg,
                obj.grade.base_price,
                deviation,
                obj.grade.minimum_price,
                obj.grade.maximum_price
            )
        return "No base price available for analysis"
    price_analysis.short_description = 'Price Analysis'
    
    actions = ['approve_transactions', 'flag_for_review', 'export_to_csv']
    
    def approve_transactions(self, request, queryset):
        updated = queryset.update(status='COMPLETED')
        self.message_user(request, f'{updated} transactions approved.')
    approve_transactions.short_description = 'Approve selected transactions'
    
    def flag_for_review(self, request, queryset):
        updated = queryset.update(is_flagged=True)
        self.message_user(request, f'{updated} transactions flagged for review.')
    flag_for_review.short_description = 'Flag for review'
    
    def export_to_csv(self, request, queryset):
        # Implementation for CSV export
        pass
    export_to_csv.short_description = 'Export to CSV'


@admin.register(DailyPrice)
class DailyPriceAdmin(admin.ModelAdmin):
    list_display = [
        'grade', 'date', 'opening_price', 'closing_price', 
        'high_price', 'low_price', 'volume_traded', 'price_change_display'
    ]
    list_filter = ['date', 'grade__category', 'floor']
    search_fields = ['grade__grade_code', 'grade__grade_name']
    readonly_fields = ['created_at', 'price_change', 'price_change_percentage']
    date_hierarchy = 'date'
    ordering = ['-date', 'grade__grade_code']
    
    def price_change_display(self, obj):
        change = obj.price_change
        change_pct = obj.price_change_percentage
        
        if change > 0:
            color = 'green'
            arrow = '↗'
        elif change < 0:
            color = 'red'
            arrow = '↘'
        else:
            color = 'gray'
            arrow = '→'
        
        return format_html(
            '<span style="color: {}; font-weight: bold;">{} ${:.2f} ({:+.1f}%)</span>',
            color, arrow, change, change_pct
        )
    price_change_display.short_description = 'Price Change'


@admin.register(SystemAlert)
class SystemAlertAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'alert_type', 'severity', 'is_active', 
        'created_at', 'resolved_by', 'resolution_time'
    ]
    list_filter = ['alert_type', 'severity', 'is_active', 'created_at']
    search_fields = ['title', 'message']
    readonly_fields = ['created_at', 'resolution_time']
    actions = ['mark_resolved', 'mark_active']
    
    def resolution_time(self, obj):
        if obj.resolved_at and obj.created_at:
            duration = obj.resolved_at - obj.created_at
            hours, remainder = divmod(duration.total_seconds(), 3600)
            minutes, _ = divmod(remainder, 60)
            return f"{int(hours)}h {int(minutes)}m"
        return "Not resolved"
    resolution_time.short_description = 'Resolution Time'
    
    def mark_resolved(self, request, queryset):
        for alert in queryset:
            alert.resolve(request.user)
        self.message_user(request, f'{queryset.count()} alerts marked as resolved.')
    mark_resolved.short_description = 'Mark as resolved'
    
    def mark_active(self, request, queryset):
        updated = queryset.update(is_active=True, resolved_at=None, resolved_by=None)
        self.message_user(request, f'{updated} alerts reactivated.')
    mark_active.short_description = 'Reactivate alerts'


@admin.register(DashboardMetric)
class DashboardMetricAdmin(admin.ModelAdmin):
    list_display = ['metric_type', 'value', 'floor', 'grade', 'timestamp']
    list_filter = ['metric_type', 'timestamp', 'floor', 'grade__category']
    search_fields = ['metric_type']
    readonly_fields = ['timestamp']
    date_hierarchy = 'timestamp'
    ordering = ['-timestamp']
    
    def get_queryset(self, request):
        # Only show recent metrics to improve performance
        return super().get_queryset(request).filter(
            timestamp__gte=timezone.now() - timedelta(days=30)
        )


@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'ip_address', 'login_time', 'last_activity', 
        'is_active', 'session_duration_display'
    ]
    list_filter = ['is_active', 'login_time', 'user__groups']
    search_fields = ['user__username', 'ip_address']
    readonly_fields = ['login_time', 'session_duration_display']
    
    def session_duration_display(self, obj):
        duration = obj.duration
        hours, remainder = divmod(duration.total_seconds(), 3600)
        minutes, _ = divmod(remainder, 60)
        return f"{int(hours)}h {int(minutes)}m"
    session_duration_display.short_description = 'Duration'
    
    def get_queryset(self, request):
        # Only show recent sessions
        return super().get_queryset(request).filter(
            login_time__gte=timezone.now() - timedelta(days=7)
        )


# Custom admin site configuration
admin.site.site_header = 'TIMB Administration'
admin.site.site_title = 'TIMB Admin'
admin.site.index_title = 'Tobacco Industry and Marketing Board'