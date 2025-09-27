from django.contrib import admin
from .models import *

@admin.register(AIModel)
class AIModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'model_type', 'version', 'status', 'accuracy', 'created_at')
    list_filter = ('model_type', 'status', 'created_at')
    search_fields = ('name', 'version')
    readonly_fields = ('encrypted_model_path',)

@admin.register(PredictionLog)
class PredictionLogAdmin(admin.ModelAdmin):
    list_display = ('prediction_type', 'model_used', 'confidence_score', 'created_at', 'user')
    list_filter = ('prediction_type', 'model_used', 'created_at')
    search_fields = ('model_used__name',)
    date_hierarchy = 'created_at'

@admin.register(ModelPerformanceMetric)
class ModelPerformanceMetricAdmin(admin.ModelAdmin):
    list_display = ('model', 'metric_name', 'metric_value', 'measurement_date')
    list_filter = ('model', 'metric_name', 'measurement_date')
    search_fields = ('model__name', 'metric_name')

@admin.register(TrainingJob)
class TrainingJobAdmin(admin.ModelAdmin):
    list_display = ('model', 'job_id', 'status', 'progress_percentage', 'started_at', 'created_by')
    list_filter = ('status', 'created_by')
    search_fields = ('job_id', 'model__name')
    readonly_fields = ('job_id',)

@admin.register(SideBuyingDetection)
class SideBuyingDetectionAdmin(admin.ModelAdmin):
    list_display = ('farmer_name', 'merchant_name', 'is_side_buying_detected', 'confidence_score', 'detection_date')
    list_filter = ('is_side_buying_detected', 'detection_date')
    search_fields = ('farmer_name', 'merchant_name')
    readonly_fields = ('risk_factors', 'contracted_quantity', 'delivered_quantity')