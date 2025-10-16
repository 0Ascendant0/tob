from django.core.management.base import BaseCommand
from django.conf import settings
import pandas as pd
import os
from ai_models.ai_engine import fraud_model, yield_model, side_buying_model, farmer_risk_model

class Command(BaseCommand):
    help = 'Train AI models with sample data'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--model',
            type=str,
            help='Specific model to train (fraud, yield, side_buying, farmer_risk)',
        )
        parser.add_argument(
            '--data-file',
            type=str,
            help='Path to training data file (CSV)',
        )
    
    def handle(self, *args, **options):
        model_type = options.get('model')
        data_file = options.get('data_file')
        
        if model_type:
            self.train_specific_model(model_type, data_file)
        else:
            self.train_all_models()

    def train_specific_model(self, model_type, data_file=None):
        """Train a specific model"""
        if model_type == 'fraud':
            self.train_fraud_model(data_file)
        elif model_type == 'yield':
            self.train_yield_model(data_file)
        elif model_type == 'side_buying':
            self.train_side_buying_model(data_file)
        elif model_type == 'farmer_risk':
            self.train_farmer_risk_model(data_file)
        else:
            self.stdout.write(self.style.ERROR(f'Unknown model type: {model_type}'))

    def train_all_models(self):
        """Train all models with sample data"""
        self.stdout.write(self.style.SUCCESS('Training all AI models...'))
        
        # Train fraud detection model
        self.train_fraud_model()
        
        # Train yield prediction model
        self.train_yield_model()
        
        # Train side buying detection model
        self.train_side_buying_model()
        
        # Train farmer risk assessment model
        self.train_farmer_risk_model()
        
        self.stdout.write(self.style.SUCCESS('All models trained successfully!'))

    def train_fraud_model(self, data_file=None):
        """Train fraud detection model"""
        self.stdout.write('Training fraud detection model...')
        
        if data_file and os.path.exists(data_file):
            data = pd.read_csv(data_file)
        else:
            # Generate sample fraud detection data
            data = self.generate_sample_fraud_data()
        
        result = fraud_model.train(data)
        
        if 'error' in result:
            self.stdout.write(self.style.ERROR(f'Error training fraud model: {result["error"]}'))
        else:
            self.stdout.write(self.style.SUCCESS(
                f'Fraud model trained successfully! Accuracy: {result["accuracy"]:.2%}'
            ))

    def train_yield_model(self, data_file=None):
        """Train yield prediction model"""
        self.stdout.write('Training yield prediction model...')
        
        if data_file and os.path.exists(data_file):
            data = pd.read_csv(data_file)
        else:
            # Generate sample yield prediction data
            data = self.generate_sample_yield_data()
        
        result = yield_model.train(data)
        
        if 'error' in result:
            self.stdout.write(self.style.ERROR(f'Error training yield model: {result["error"]}'))
        else:
            self.stdout.write(self.style.SUCCESS(
                f'Yield model trained successfully! MAE: {result["mae"]:.2f}'
            ))

    def train_side_buying_model(self, data_file=None):
        """Train side buying detection model"""
        self.stdout.write('Training side buying detection model...')
        
        if data_file and os.path.exists(data_file):
            data = pd.read_csv(data_file)
        else:
            # Generate sample side buying data
            data = self.generate_sample_side_buying_data()
        
        result = side_buying_model.train(data)
        
        if 'error' in result:
            self.stdout.write(self.style.ERROR(f'Error training side buying model: {result["error"]}'))
        else:
            self.stdout.write(self.style.SUCCESS(
                f'Side buying model trained successfully! Accuracy: {result["accuracy"]:.2%}'
            ))

    def train_farmer_risk_model(self, data_file=None):
        """Train farmer risk assessment model"""
        self.stdout.write('Training farmer risk assessment model...')
        
        if data_file and os.path.exists(data_file):
            data = pd.read_csv(data_file)
        else:
            # Generate sample farmer risk data
            data = self.generate_sample_farmer_risk_data()
        
        result = farmer_risk_model.train(data)
        
        if 'error' in result:
            self.stdout.write(self.style.ERROR(f'Error training farmer risk model: {result["error"]}'))
        else:
            self.stdout.write(self.style.SUCCESS(
                f'Farmer risk model trained successfully! Accuracy: {result["accuracy"]:.2%}'
            ))

    def generate_sample_fraud_data(self):
        """Generate sample fraud detection data"""
        import numpy as np
        
        np.random.seed(42)
        n_samples = 1000
        
        data = pd.DataFrame({
            'grade': np.random.choice(['A1', 'B1', 'C1', 'X1', 'P1'], n_samples),
            'purchase_price_per_kg': np.random.normal(2.5, 0.5, n_samples),
            'sale_price_per_kg': np.random.normal(3.0, 0.6, n_samples),
            'quantity_kg': np.random.exponential(1000, n_samples),
            'time_difference_days': np.random.exponential(2, n_samples),
            'merchant_experience_years': np.random.randint(1, 20, n_samples),
            'market_volatility': np.random.uniform(0.1, 0.3, n_samples),
            'season': np.random.choice(['peak', 'off-peak', 'transition'], n_samples),
            'floor_location': np.random.choice(['harare', 'bulawayo', 'mutare'], n_samples),
        })
        
        # Calculate price markup ratio
        data['price_markup_ratio'] = data['sale_price_per_kg'] / data['purchase_price_per_kg']
        
        # Generate fraud labels based on rules
        fraud_conditions = (
            (data['price_markup_ratio'] > 2.0) |
            (data['quantity_kg'] > 5000) |
            (data['time_difference_days'] < 0.1) |
            (data['merchant_experience_years'] < 2)
        )
        
        data['is_fraud'] = fraud_conditions.astype(int)
        
        return data

    def generate_sample_yield_data(self):
        """Generate sample yield prediction data"""
        import numpy as np
        
        np.random.seed(42)
        n_samples = 500
        
        data = pd.DataFrame({
            'rainfall_mm': np.random.normal(650, 150, n_samples),
            'temperature_avg': np.random.normal(23.5, 3, n_samples),
            'number_of_farmers': np.random.randint(50000, 100000, n_samples),
            'total_hectarage': np.random.normal(180000, 20000, n_samples),
            'inflation_rate': np.random.uniform(10, 25, n_samples),
            'interest_rate': np.random.uniform(20, 35, n_samples),
        })
        
        # Generate yield based on factors
        base_yield = 1800  # kg per hectare
        rainfall_factor = np.clip(data['rainfall_mm'] / 650, 0.5, 1.5)
        temp_factor = np.where(
            (data['temperature_avg'] >= 20) & (data['temperature_avg'] <= 28),
            1.0, 0.8
        )
        farmer_factor = np.clip(data['number_of_farmers'] / 75000, 0.8, 1.2)
        
        data['predicted_yield'] = (
            base_yield * rainfall_factor * temp_factor * farmer_factor +
            np.random.normal(0, 200, n_samples)
        )
        
        return data

    def generate_sample_side_buying_data(self):
        """Generate sample side buying detection data"""
        import numpy as np
        
        np.random.seed(42)
        n_samples = 800
        
        data = pd.DataFrame({
            'contracted_quantity_kg': np.random.exponential(2000, n_samples),
            'delivered_to_contractor_kg': np.random.exponential(1500, n_samples),
            'delivered_to_others_kg': np.random.exponential(300, n_samples),
            'distance_to_contractor_km': np.random.exponential(15, n_samples),
            'distance_to_alternative_km': np.random.exponential(20, n_samples),
            'alternative_price_premium': np.random.uniform(0, 0.3, n_samples),
            'farmer_debt_level_usd': np.random.exponential(500, n_samples),
            'contractor_support_score': np.random.randint(30, 100, n_samples),
            'harvest_season': np.random.choice(['early', 'mid', 'late'], n_samples),
        })
        
        # Calculate delivery ratio
        data['delivery_ratio'] = data['delivered_to_contractor_kg'] / data['contracted_quantity_kg']
        
        # Generate side buying labels based on rules
        side_buying_conditions = (
            (data['delivery_ratio'] < 0.7) |
            (data['alternative_price_premium'] > 0.2) |
            (data['contractor_support_score'] < 50) |
            (data['farmer_debt_level_usd'] > 1000)
        )
        
        data['is_side_buying'] = side_buying_conditions.astype(int)
        
        return data

    def generate_sample_farmer_risk_data(self):
        """Generate sample farmer risk assessment data"""
        import numpy as np
        
        np.random.seed(42)
        n_samples = 1200
        
        data = pd.DataFrame({
            'loan_amount': np.random.exponential(5000, n_samples),
            'hectarage': np.random.uniform(1, 10, n_samples),
            'yields': np.random.normal(1500, 300, n_samples),
            'yield_per_ha': np.random.normal(1800, 400, n_samples),
            'loan_per_ha': np.random.exponential(2000, n_samples),
            'side_marketer_effect': np.random.uniform(0, 0.5, n_samples),
            'merchant_contractor': np.random.choice(['ABC Tobacco', 'XYZ Trading', 'Green Leaf Co'], n_samples),
            'mass_usually_produced_kg': np.random.exponential(2000, n_samples),
            'default_prob': np.random.uniform(0, 0.3, n_samples),
            'location': np.random.choice(['Mashonaland', 'Matabeleland', 'Masvingo'], n_samples),
            'gender': np.random.choice(['Male', 'Female'], n_samples),
            'grade_normally_produced': np.random.choice(['Flue Cured', 'Burley', 'Oriental'], n_samples),
        })
        
        # Generate risk labels based on rules
        risk_conditions = (
            (data['loan_per_ha'] > 3000) |
            (data['default_prob'] > 0.2) |
            (data['side_marketer_effect'] > 0.3) |
            (data['yield_per_ha'] < 1200)
        )
        
        data['is_risky'] = risk_conditions.astype(int)
        
        return data