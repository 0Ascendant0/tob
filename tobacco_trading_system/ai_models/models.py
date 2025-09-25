from django.db import models
from django.contrib.auth import get_user_model
from utils.encryption import encryption

User = get_user_model()

class YieldPredictionData(models.Model):
    year = models.IntegerField(unique=True)
    rainfall_mm = models.DecimalField(max_digits=8, decimal_places=2)
    temperature_avg = models.DecimalField(max_digits=5, decimal_places=2)
    number_of_farmers = models.IntegerField()
    total_hectarage = models.DecimalField(max_digits=12, decimal_places=2)
    predicted_yield = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    actual_yield = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    economic_factors = models.JSONField(default=dict)  # Interest rates, inflation, etc.
    encrypted_additional_data = models.TextField(blank=True)
    prediction_accuracy = models.FloatField(null=True, blank=True)  # Calculated after actual yield is known
    
    def set_additional_data(self, data):
        self.encrypted_additional_data = encryption.encrypt_data(data)
    
    def get_additional_data(self):
        if self.encrypted_additional_data:
            return encryption.decrypt_data(self.encrypted_additional_data)
        return {}

class FraudDetectionModel(models.Model):
    model_name = models.CharField(max_length=100)
    model_version = models.CharField(max_length=20)
    encrypted_model_parameters = models.TextField()
    training_accuracy = models.FloatField()
    validation_accuracy = models.FloatField()
    false_positive_rate = models.FloatField()
    false_negative_rate = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=False)
    
    def set_model_parameters(self, parameters):
        self.encrypted_model_parameters = encryption.encrypt_data(parameters)
    
    def get_model_parameters(self):
        if self.encrypted_model_parameters:
            return encryption.decrypt_data(self.encrypted_model_parameters)
        return {}

class PredictionLog(models.Model):
    PREDICTION_TYPES = [
        ('YIELD', 'Yield Prediction'),
        ('FRAUD', 'Fraud Detection'),
        ('PRICE', 'Price Prediction'),
        ('DEMAND', 'Demand Prediction'),
        ('RISK', 'Risk Assessment'),
    ]
    
    prediction_type = models.CharField(max_length=20, choices=PREDICTION_TYPES)
    model_used = models.CharField(max_length=100)
    input_data = models.JSONField()
    prediction_result = models.JSONField()
    confidence_score = models.FloatField()
    encrypted_detailed_analysis = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    def set_detailed_analysis(self, analysis):
        self.encrypted_detailed_analysis = encryption.encrypt_data(analysis)
    
    def get_detailed_analysis(self):
        if self.encrypted_detailed_analysis:
            return encryption.decrypt_data(self.encrypted_detailed_analysis)
        return {}

class ModelPerformanceMetric(models.Model):
    model_name = models.CharField(max_length=100)
    metric_name = models.CharField(max_length=50)
    metric_value = models.FloatField()
    measurement_date = models.DateTimeField(auto_now_add=True)
    encrypted_metadata = models.TextField(blank=True)
    
    def set_metadata(self, metadata):
        self.encrypted_metadata = encryption.encrypt_data(metadata)
    
    def get_metadata(self):
        if self.encrypted_metadata:
            return encryption.decrypt_data(self.encrypted_metadata)
        return {}