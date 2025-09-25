from django.db import models
from django.contrib.auth import get_user_model
from timb_dashboard.models import TobaccoFloor, TobaccoGrade
from utils.encryption import encryption

User = get_user_model()

class RealTimePrice(models.Model):
    floor = models.ForeignKey(TobaccoFloor, on_delete=models.CASCADE)
    grade = models.ForeignKey(TobaccoGrade, on_delete=models.CASCADE)
    current_price = models.DecimalField(max_digits=10, decimal_places=2)
    previous_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    price_change = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    volume_traded_today = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    last_updated = models.DateTimeField(auto_now=True)
    encrypted_market_data = models.TextField(blank=True)
    
    def set_market_data(self, data):
        self.encrypted_market_data = encryption.encrypt_data(data)
    
    def get_market_data(self):
        if self.encrypted_market_data:
            return encryption.decrypt_data(self.encrypted_market_data)
        return {}
    
    class Meta:
        unique_together = ['floor', 'grade']

class LiveTransaction(models.Model):
    transaction_id = models.CharField(max_length=50, unique=True)
    floor = models.ForeignKey(TobaccoFloor, on_delete=models.CASCADE)
    grade = models.ForeignKey(TobaccoGrade, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    buyer_info = models.CharField(max_length=200)  # Anonymized
    seller_info = models.CharField(max_length=200)  # Anonymized
    timestamp = models.DateTimeField(auto_now_add=True)
    is_broadcast = models.BooleanField(default=False)

class MarketAlert(models.Model):
    ALERT_TYPES = [
        ('PRICE_SPIKE', 'Price Spike'),
        ('VOLUME_SURGE', 'Volume Surge'),
        ('MARKET_CLOSURE', 'Market Closure'),
        ('GRADE_SHORTAGE', 'Grade Shortage'),
        ('FRAUD_DETECTED', 'Fraud Detected'),
    ]
    
    alert_type = models.CharField(max_length=20, choices=ALERT_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    severity = models.CharField(max_length=20, choices=[
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('CRITICAL', 'Critical')
    ])
    floor = models.ForeignKey(TobaccoFloor, on_delete=models.CASCADE, null=True, blank=True)
    grade = models.ForeignKey(TobaccoGrade, on_delete=models.CASCADE, null=True, blank=True)
    encrypted_alert_data = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_resolved = models.BooleanField(default=False)
    
    def set_alert_data(self, data):
        self.encrypted_alert_data = encryption.encrypt_data(data)
    
    def get_alert_data(self):
        if self.encrypted_alert_data:
            return encryption.decrypt_data(self.encrypted_alert_data)
        return {}

class SystemNotification(models.Model):
    recipient = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(max_length=50)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    encrypted_metadata = models.TextField(blank=True)
    
    def set_metadata(self, metadata):
        self.encrypted_metadata = encryption.encrypt_data(metadata)
    
    def get_metadata(self):
        if self.encrypted_metadata:
            return encryption.decrypt_data(self.encrypted_metadata)
        return {}