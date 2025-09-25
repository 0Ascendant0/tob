from django.db import models
from django.contrib.auth import get_user_model
from utils.encryption import encryption
import json

User = get_user_model()

class TobaccoGrade(models.Model):
    GRADE_CATEGORIES = [
        ('STRIP', 'Strip Grades (A)'),
        ('LEAF', 'Leaf Grades (L)'),
        ('LUG', 'Lug Grades (X)'),
        ('TIP', 'Tip Grades (T)'),
        ('SMOKING', 'Smoking Grades (H)'),
        ('CUTTER', 'Cutter Grades (C)'),
        ('SCRAP', 'Scrap Grades (B)'),
        ('OTHER', 'Other Grades'),
    ]
    
    grade_code = models.CharField(max_length=20, unique=True)
    grade_name = models.CharField(max_length=100)
    category = models.CharField(max_length=20, choices=GRADE_CATEGORIES)
    description = models.TextField(blank=True)
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

class Merchant(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=200)
    license_number = models.CharField(max_length=100, unique=True)
    encrypted_business_data = models.TextField()  # Encrypted sensitive business data
    registration_date = models.DateField()
    status = models.CharField(max_length=20, choices=[
        ('ACTIVE', 'Active'),
        ('SUSPENDED', 'Suspended'),
        ('PENDING', 'Pending Approval')
    ], default='PENDING')
    risk_score = models.FloatField(default=0.0)
    
    def set_business_data(self, data):
        self.encrypted_business_data = encryption.encrypt_data(data)
    
    def get_business_data(self):
        if self.encrypted_business_data:
            return encryption.decrypt_data(self.encrypted_business_data)
        return {}

class TobaccoFloor(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=200)
    capacity = models.IntegerField()  # in kg
    is_active = models.BooleanField(default=True)
    manager = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('FLOOR_SALE', 'Floor Sale'),
        ('MERCHANT_TO_MERCHANT', 'Merchant to Merchant'),
        ('EXPORT', 'Export'),
        ('SIDE_PURCHASE', 'Side Purchase'),
    ]
    
    transaction_id = models.CharField(max_length=50, unique=True)
    transaction_type = models.CharField(max_length=30, choices=TRANSACTION_TYPES)
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sales')
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='purchases')
    floor = models.ForeignKey(TobaccoFloor, on_delete=models.SET_NULL, null=True, blank=True)
    grade = models.ForeignKey(TobaccoGrade, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)  # in kg
    price_per_kg = models.DecimalField(max_digits=10, decimal_places=2)
    total_amount = models.DecimalField(max_digits=15, decimal_places=2)
    encrypted_transaction_details = models.TextField()  # Encrypted additional details
    timestamp = models.DateTimeField(auto_now_add=True)
    is_flagged = models.BooleanField(default=False)
    fraud_score = models.FloatField(default=0.0)
    
    def set_transaction_details(self, details):
        self.encrypted_transaction_details = encryption.encrypt_data(details)
    
    def get_transaction_details(self):
        if self.encrypted_transaction_details:
            return encryption.decrypt_data(self.encrypted_transaction_details)
        return {}

class ContractFarmer(models.Model):
    farmer_id = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    phone = models.CharField(max_length=15)
    contracted_merchant = models.ForeignKey(Merchant, on_delete=models.CASCADE)
    contract_start_date = models.DateField()
    contract_end_date = models.DateField()
    contracted_quantity = models.DecimalField(max_digits=10, decimal_places=2)  # in kg
    delivered_quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    encrypted_farmer_data = models.TextField()  # Encrypted personal data
    risk_score = models.FloatField(default=0.0)
    
    def set_farmer_data(self, data):
        self.encrypted_farmer_data = encryption.encrypt_data(data)
    
    def get_farmer_data(self):
        if self.encrypted_farmer_data:
            return encryption.decrypt_data(self.encrypted_farmer_data)
        return {}

class PriceHistory(models.Model):
    grade = models.ForeignKey(TobaccoGrade, on_delete=models.CASCADE)
    floor = models.ForeignKey(TobaccoFloor, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    session = models.CharField(max_length=20)  # Morning, Afternoon
    volume_traded = models.DecimalField(max_digits=10, decimal_places=2)

class FraudAlert(models.Model):
    ALERT_TYPES = [
        ('PRICE_MANIPULATION', 'Price Manipulation'),
        ('SIDE_BUYING', 'Side Buying'),
        ('QUANTITY_MISMATCH', 'Quantity Mismatch'),
        ('UNUSUAL_PATTERN', 'Unusual Trading Pattern'),
    ]
    
    alert_type = models.CharField(max_length=30, choices=ALERT_TYPES)
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, null=True, blank=True)
    merchant = models.ForeignKey(Merchant, on_delete=models.CASCADE, null=True, blank=True)
    farmer = models.ForeignKey(ContractFarmer, on_delete=models.CASCADE, null=True, blank=True)
    severity = models.CharField(max_length=20, choices=[
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('CRITICAL', 'Critical')
    ])
    description = models.TextField()
    encrypted_evidence = models.TextField()  # Encrypted evidence data
    created_at = models.DateTimeField(auto_now_add=True)
    investigated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, choices=[
        ('OPEN', 'Open'),
        ('INVESTIGATING', 'Under Investigation'),
        ('RESOLVED', 'Resolved'),
        ('FALSE_POSITIVE', 'False Positive')
    ], default='OPEN')
    
    def set_evidence(self, evidence):
        self.encrypted_evidence = encryption.encrypt_data(evidence)
    
    def get_evidence(self):
        if self.encrypted_evidence:
            return encryption.decrypt_data(self.encrypted_evidence)
        return {}