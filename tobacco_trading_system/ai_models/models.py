from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal
from utils.encryption import encryption
import json

User = get_user_model()

class AIModel(models.Model):
    """AI Model registry and metadata"""
    
    MODEL_TYPES = [
        ('FRAUD_DETECTION', 'Fraud Detection'),
        ('YIELD_PREDICTION', 'Yield Prediction'),
        ('PRICE_PREDICTION', 'Price Prediction'),
        ('SIDE_BUYING_DETECTION', 'Side Buying Detection'),
        ('RISK_ASSESSMENT', 'Risk Assessment'),
    ]
    
    STATUS_CHOICES = [
        ('TRAINING', 'Training'),
        ('ACTIVE', 'Active'),
        ('DEPRECATED', 'Deprecated'),
        ('ERROR', 'Error'),
    ]
    
    name = models.CharField(max_length=100)
    model_type = models.CharField(max_length=30, choices=MODEL_TYPES)
    version = models.CharField(max_length=20)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='TRAINING')
    
    # Performance metrics
    accuracy = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    precision = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    recall = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    f1_score = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    
    # Training information
    training_data_size = models.IntegerField(default=0)
    training_started = models.DateTimeField(blank=True, null=True)
    training_completed = models.DateTimeField(blank=True, null=True)
    
    # Model file path (encrypted for security)
    encrypted_model_path = models.TextField(blank=True)
    
    # Metadata
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['name', 'version']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} v{self.version}"
    
    def set_model_path(self, path):
        """Encrypt and store model file path"""
        self.encrypted_model_path = encryption.encrypt_data(path)
    
    def get_model_path(self):
        """Decrypt and return model file path"""
        if self.encrypted_model_path:
            return encryption.decrypt_data(self.encrypted_model_path)
        return ""

class PredictionLog(models.Model):
    """Log of AI predictions made"""
    
    PREDICTION_TYPES = [
        ('FRAUD', 'Fraud Detection'),
        ('YIELD', 'Yield Prediction'),
        ('PRICE', 'Price Prediction'),
        ('SIDE_BUYING', 'Side Buying Detection'),
        ('RISK', 'Risk Assessment'),
    ]
    
    prediction_type = models.CharField(max_length=20, choices=PREDICTION_TYPES)
    model_used = models.ForeignKey(AIModel, on_delete=models.CASCADE)
    input_data = models.JSONField()
    prediction_result = models.JSONField()
    confidence_score = models.DecimalField(max_digits=5, decimal_places=3)
    
    # Context
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    related_object_id = models.CharField(max_length=100, blank=True)
    related_object_type = models.CharField(max_length=50, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['prediction_type', 'created_at']),
            models.Index(fields=['model_used', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.get_prediction_type_display()} - {self.confidence_score}"

class ModelPerformanceMetric(models.Model):
    """Track model performance over time"""
    
    model = models.ForeignKey(AIModel, on_delete=models.CASCADE, related_name='performance_metrics')
    metric_name = models.CharField(max_length=50)
    metric_value = models.DecimalField(max_digits=10, decimal_places=4)
    measurement_date = models.DateTimeField(auto_now_add=True)
    
    # Additional context
    test_data_size = models.IntegerField(default=0)
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-measurement_date']
        indexes = [
            models.Index(fields=['model', 'measurement_date']),
            models.Index(fields=['metric_name', 'measurement_date']),
        ]
    
    def __str__(self):
        return f"{self.model.name} - {self.metric_name}: {self.metric_value}"

class TrainingJob(models.Model):
    """Track model training jobs"""
    
    STATUS_CHOICES = [
        ('QUEUED', 'Queued'),
        ('RUNNING', 'Running'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    model = models.ForeignKey(AIModel, on_delete=models.CASCADE, related_name='training_jobs')
    job_id = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='QUEUED')
    
    # Training parameters
    training_parameters = models.JSONField(default=dict)
    dataset_version = models.CharField(max_length=50, blank=True)
    
    # Progress tracking
    progress_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    current_epoch = models.IntegerField(default=0)
    total_epochs = models.IntegerField(default=100)
    
    # Results
    final_accuracy = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    training_loss = models.DecimalField(max_digits=10, decimal_places=6, blank=True, null=True)
    validation_loss = models.DecimalField(max_digits=10, decimal_places=6, blank=True, null=True)
    
    # Timing
    started_at = models.DateTimeField(blank=True, null=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    estimated_completion = models.DateTimeField(blank=True, null=True)
    
    # Error handling
    error_message = models.TextField(blank=True)
    
    # Audit
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Training Job {self.job_id} - {self.model.name}"
    
    @property
    def duration(self):
        """Calculate training duration"""
        if self.started_at and self.completed_at:
            return self.completed_at - self.started_at
        elif self.started_at:
            return timezone.now() - self.started_at
        return None

class SideBuyingDetection(models.Model):
    """Side buying detection results"""
    
    farmer_name = models.CharField(max_length=200)
    farmer_id = models.CharField(max_length=50)
    merchant_name = models.CharField(max_length=200)
    
    # Detection results
    is_side_buying_detected = models.BooleanField(default=False)
    confidence_score = models.DecimalField(max_digits=5, decimal_places=3)
    risk_factors = models.JSONField(default=list)
    
    # Contract details
    contracted_quantity = models.DecimalField(max_digits=10, decimal_places=2)
    delivered_quantity = models.DecimalField(max_digits=10, decimal_places=2)
    delivery_ratio = models.DecimalField(max_digits=5, decimal_places=3)
    
    # Market analysis
    market_price_deviation = models.DecimalField(max_digits=5, decimal_places=3, blank=True, null=True)
    alternative_sales_detected = models.BooleanField(default=False)
    
    # Metadata
    detection_date = models.DateTimeField(auto_now_add=True)
    model_version = models.CharField(max_length=20)
    
    class Meta:
        ordering = ['-detection_date']
        indexes = [
            models.Index(fields=['is_side_buying_detected', 'detection_date']),
            models.Index(fields=['farmer_id', 'detection_date']),
        ]
    
    def __str__(self):
        return f"Side Buying Detection - {self.farmer_name} ({self.confidence_score})"