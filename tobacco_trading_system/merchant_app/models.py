from django.db import models
from django.contrib.auth import get_user_model
from timb_dashboard.models import TobaccoGrade, Merchant, Transaction
from utils.encryption import encryption

User = get_user_model()

class MerchantInventory(models.Model):
    merchant = models.ForeignKey(Merchant, on_delete=models.CASCADE)
    grade = models.ForeignKey(TobaccoGrade, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    average_cost = models.DecimalField(max_digits=10, decimal_places=2)
    location = models.CharField(max_length=200)
    encrypted_storage_details = models.TextField()  # Encrypted storage conditions, etc.
    last_updated = models.DateTimeField(auto_now=True)
    
    def set_storage_details(self, details):
        self.encrypted_storage_details = encryption.encrypt_data(details)
    
    def get_storage_details(self):
        if self.encrypted_storage_details:
            return encryption.decrypt_data(self.encrypted_storage_details)
        return {}
    
    class Meta:
        unique_together = ['merchant', 'grade', 'location']

class CustomGrade(models.Model):
    merchant = models.ForeignKey(Merchant, on_delete=models.CASCADE)
    custom_grade_name = models.CharField(max_length=100)
    description = models.TextField()
    target_price = models.DecimalField(max_digits=10, decimal_places=2)
    encrypted_composition = models.TextField()  # Encrypted grade composition rules
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    def set_composition(self, composition):
        """Set the composition rules for this custom grade"""
        self.encrypted_composition = encryption.encrypt_data(composition)
    
    def get_composition(self):
        """Get the composition rules for this custom grade"""
        if self.encrypted_composition:
            return encryption.decrypt_data(self.encrypted_composition)
        return {}

class CustomGradeComponent(models.Model):
    custom_grade = models.ForeignKey(CustomGrade, on_delete=models.CASCADE, related_name='components')
    base_grade = models.ForeignKey(TobaccoGrade, on_delete=models.CASCADE)
    percentage = models.DecimalField(max_digits=5, decimal_places=2)  # 0.00 to 100.00
    minimum_quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0)

class ClientOrder(models.Model):
    ORDER_STATUS = [
        ('PENDING', 'Pending'),
        ('PROCESSING', 'Processing'),
        ('PARTIALLY_FILLED', 'Partially Filled'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    merchant = models.ForeignKey(Merchant, on_delete=models.CASCADE)
    order_number = models.CharField(max_length=50, unique=True)
    client_name = models.CharField(max_length=200)
    encrypted_client_details = models.TextField()  # Encrypted client information
    custom_grade = models.ForeignKey(CustomGrade, on_delete=models.CASCADE, null=True, blank=True)
    requested_quantity = models.DecimalField(max_digits=10, decimal_places=2)
    filled_quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    target_price = models.DecimalField(max_digits=10, decimal_places=2)
    delivery_date = models.DateField()
    status = models.CharField(max_length=20, choices=ORDER_STATUS, default='PENDING')
    encrypted_special_requirements = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def set_client_details(self, details):
        self.encrypted_client_details = encryption.encrypt_data(details)
    
    def get_client_details(self):
        if self.encrypted_client_details:
            return encryption.decrypt_data(self.encrypted_client_details)
        return {}
    
    def set_special_requirements(self, requirements):
        self.encrypted_special_requirements = encryption.encrypt_data(requirements)
    
    def get_special_requirements(self):
        if self.encrypted_special_requirements:
            return encryption.decrypt_data(self.encrypted_special_requirements)
        return {}

class PurchaseRecommendation(models.Model):
    merchant = models.ForeignKey(Merchant, on_delete=models.CASCADE)
    grade = models.ForeignKey(TobaccoGrade, on_delete=models.CASCADE)
    recommended_quantity = models.DecimalField(max_digits=10, decimal_places=2)
    recommended_price = models.DecimalField(max_digits=10, decimal_places=2)
    confidence_score = models.FloatField()  # 0.0 to 1.0
    reasoning = models.TextField()
    encrypted_ai_analysis = models.TextField()  # Detailed AI analysis
    created_at = models.DateTimeField(auto_now_add=True)
    is_acted_upon = models.BooleanField(default=False)
    
    def set_ai_analysis(self, analysis):
        self.encrypted_ai_analysis = encryption.encrypt_data(analysis)
    
    def get_ai_analysis(self):
        if self.encrypted_ai_analysis:
            return encryption.decrypt_data(self.encrypted_ai_analysis)
        return {}

class RiskAssessment(models.Model):
    RISK_TYPES = [
        ('MARKET', 'Market Risk'),
        ('PRICE', 'Price Risk'),
        ('SUPPLY', 'Supply Risk'),
        ('DEMAND', 'Demand Risk'),
        ('FARMER', 'Farmer Risk'),
    ]
    
    merchant = models.ForeignKey(Merchant, on_delete=models.CASCADE)
    risk_type = models.CharField(max_length=20, choices=RISK_TYPES)
    risk_level = models.CharField(max_length=20, choices=[
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('CRITICAL', 'Critical')
    ])
    risk_score = models.FloatField()  # 0.0 to 100.0
    description = models.TextField()
    encrypted_mitigation_strategies = models.TextField()
    assessment_date = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    def set_mitigation_strategies(self, strategies):
        self.encrypted_mitigation_strategies = encryption.encrypt_data(strategies)
    
    def get_mitigation_strategies(self):
        if self.encrypted_mitigation_strategies:
            return encryption.decrypt_data(self.encrypted_mitigation_strategies)
        return {}

class AggregationRule(models.Model):
    merchant = models.ForeignKey(Merchant, on_delete=models.CASCADE)
    rule_name = models.CharField(max_length=100)
    encrypted_rule_logic = models.TextField()  # Complex aggregation rules
    target_grade = models.ForeignKey(CustomGrade, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def set_rule_logic(self, logic):
        self.encrypted_rule_logic = encryption.encrypt_data(logic)
    
    def get_rule_logic(self):
        if self.encrypted_rule_logic:
            return encryption.decrypt_data(self.encrypted_rule_logic)
        return {}