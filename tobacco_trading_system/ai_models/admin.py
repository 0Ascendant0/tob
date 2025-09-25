from django.contrib import admin
from .models import *

@admin.register(YieldPredictionData)
class YieldPredictionDataAdmin(admin.ModelAdmin):
    list_display = ('year', 'rainfall_mm', 'temperature_avg', 'number_of_farmers', 'predicted_yield', 'actual_yield', 'prediction_accuracy')
    list_filter = ('year',)
    search_fields = ('year',)
    readonly_fields = ('encrypted_additional_data', 'prediction_accuracy')
    
    fieldsets = (
        ('Year & Environment', {
            'fields': ('year', 'rainfall_mm', 'temperature_avg')
        }),
        ('Farming Data', {
            'fields': ('number_of_farmers', 'total_hectarage')
        }),
        ('Yield Data', {
            'fields': ('predicted_yield', 'actual_yield', 'prediction_accuracy')
        }),
        ('Economic Factors', {
            'fields': ('economic_factors',)
        }),
        ('Additional Data', {
            'fields': ('encrypted_additional_data',),
            'classes': ('collapse',)
        }),
    )

@admin.register(FraudDetectionModel)
class FraudDetectionModelAdmin(admin.ModelAdmin):
    list_display = ('model_name', 'model_version', 'training_accuracy', 'validation_accuracy', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('model_name', 'model_version')
    readonly_fields = ('encrypted_model_parameters',)

@admin.register(PredictionLog)
class PredictionLogAdmin(admin.ModelAdmin):
    list_display = ('prediction_type', 'model_used', 'confidence_score', 'created_at', 'created_by')
    list_filter = ('prediction_type', 'model_used', 'created_at')
    search_fields = ('model_used',)
    readonly_fields = ('encrypted_detailed_analysis',)
    date_hierarchy = 'created_at'

@admin.register(ModelPerformanceMetric)
class ModelPerformanceMetricAdmin(admin.ModelAdmin):
    list_display = ('model_name', 'metric_name', 'metric_value', 'measurement_date')
    list_filter = ('model_name', 'metric_name', 'measurement_date')
    search_fields = ('model_name', 'metric_name')
    readonly_fields = ('encrypted_metadata',)