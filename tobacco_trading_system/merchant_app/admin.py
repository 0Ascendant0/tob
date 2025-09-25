from django.contrib import admin
from .models import *

@admin.register(MerchantInventory)
class MerchantInventoryAdmin(admin.ModelAdmin):
    list_display = ('merchant', 'grade', 'quantity', 'average_cost', 'location', 'last_updated')
    list_filter = ('merchant', 'grade__category', 'location')
    search_fields = ('merchant__company_name', 'grade__grade_name', 'location')
    readonly_fields = ('encrypted_storage_details',)
    
    fieldsets = (
        ('Inventory Information', {
            'fields': ('merchant', 'grade', 'quantity', 'average_cost', 'location')
        }),
        ('Storage Details', {
            'fields': ('encrypted_storage_details',),
            'classes': ('collapse',)
        }),
    )

@admin.register(CustomGrade)
class CustomGradeAdmin(admin.ModelAdmin):
    list_display = ('merchant', 'custom_grade_name', 'target_price', 'is_active', 'created_at')
    list_filter = ('merchant', 'is_active', 'created_at')
    search_fields = ('custom_grade_name', 'merchant__company_name')
    readonly_fields = ('encrypted_composition',)
    
    fieldsets = (
        ('Grade Information', {
            'fields': ('merchant', 'custom_grade_name', 'description', 'target_price', 'is_active')
        }),
        ('Composition', {
            'fields': ('encrypted_composition',),
            'classes': ('collapse',)
        }),
    )

@admin.register(CustomGradeComponent)
class CustomGradeComponentAdmin(admin.ModelAdmin):
    list_display = ('custom_grade', 'base_grade', 'percentage', 'minimum_quantity')
    list_filter = ('custom_grade__merchant', 'base_grade__category')

@admin.register(ClientOrder)
class ClientOrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'merchant', 'client_name', 'requested_quantity', 'filled_quantity', 'status', 'delivery_date')
    list_filter = ('status', 'merchant', 'delivery_date')
    search_fields = ('order_number', 'client_name', 'merchant__company_name')
    readonly_fields = ('encrypted_client_details', 'encrypted_special_requirements')
    
    fieldsets = (
        ('Order Information', {
            'fields': ('order_number', 'merchant', 'client_name', 'custom_grade')
        }),
        ('Quantities & Pricing', {
            'fields': ('requested_quantity', 'filled_quantity', 'target_price')
        }),
        ('Status & Delivery', {
            'fields': ('status', 'delivery_date')
        }),
        ('Encrypted Data', {
            'fields': ('encrypted_client_details', 'encrypted_special_requirements'),
            'classes': ('collapse',)
        }),
    )

@admin.register(PurchaseRecommendation)
class PurchaseRecommendationAdmin(admin.ModelAdmin):
    list_display = ('merchant', 'grade', 'recommended_quantity', 'recommended_price', 'confidence_score', 'is_acted_upon', 'created_at')
    list_filter = ('merchant', 'is_acted_upon', 'created_at')
    search_fields = ('merchant__company_name', 'grade__grade_name', 'reasoning')
    readonly_fields = ('encrypted_ai_analysis',)

@admin.register(RiskAssessment)
class RiskAssessmentAdmin(admin.ModelAdmin):
    list_display = ('merchant', 'risk_type', 'risk_level', 'risk_score', 'is_active', 'assessment_date')
    list_filter = ('risk_type', 'risk_level', 'is_active', 'assessment_date')
    search_fields = ('merchant__company_name', 'description')
    readonly_fields = ('encrypted_mitigation_strategies',)

@admin.register(AggregationRule)
class AggregationRuleAdmin(admin.ModelAdmin):
    list_display = ('merchant', 'rule_name', 'target_grade', 'is_active', 'created_at')
    list_filter = ('merchant', 'is_active', 'created_at')
    search_fields = ('rule_name', 'merchant__company_name')
    readonly_fields = ('encrypted_rule_logic',)