import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
from django.core.management.base import BaseCommand
from django.conf import settings

class Command(BaseCommand):
    help = 'Generate synthetic data for AI models'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--yield-years',
            type=int,
            default=40,
            help='Number of years of yield data to generate'
        )
        parser.add_argument(
            '--fraud-samples',
            type=int,
            default=10000,
            help='Number of fraud detection samples to generate'
        )
        parser.add_argument(
            '--side-buying-samples',
            type=int,
            default=5000,
            help='Number of side buying samples to generate'
        )
        parser.add_argument(
            '--risk-samples',
            type=int,
            default=10000,
            help='Number of risk modeling samples to generate'
        )
    
    def handle(self, *args, **options):
        # Create data directory
        output_dir = os.path.join(settings.BASE_DIR, 'data')
        os.makedirs(output_dir, exist_ok=True)
        
        self.stdout.write(f'Generating synthetic data in {output_dir}...')
        
        # Generate all datasets
        self.generate_yield_data(output_dir, options['yield_years'])
        self.generate_fraud_data(output_dir, options['fraud_samples'])
        self.generate_side_buying_data(output_dir, options['side_buying_samples'])
        self.generate_risk_data(output_dir, options['risk_samples'])
        
        self.stdout.write(
            self.style.SUCCESS('Successfully generated all synthetic data')
        )
    
    def generate_yield_data(self, output_dir, num_years):
        """Generate yield prediction data"""
        self.stdout.write('Generating yield prediction data...')
        
        start_year = datetime.now().year - num_years
        years = list(range(start_year, datetime.now().year + 1))
        
        data = []
        base_yield = 2500000  # Base yield in kg
        
        for year in years:
            # Simulate rainfall (300-1200mm annually)
            rainfall = np.random.normal(650, 150)
            rainfall = max(300, min(1200, rainfall))
            
            # Simulate temperature (18-28°C average)
            temperature = np.random.normal(23, 2.5)
            temperature = max(18, min(28, temperature))
            
            # Number of farmers (increasing over time with some variation)
            base_farmers = 50000 + (year - start_year) * 500
            farmers = int(np.random.normal(base_farmers, base_farmers * 0.1))
            
            # Total hectarage
            avg_hectarage_per_farmer = np.random.normal(2.5, 0.8)
            total_hectarage = farmers * max(0.1, avg_hectarage_per_farmer)
            
            # Economic factors
            inflation_rate = np.random.normal(15, 8)  # Zimbabwe inflation
            interest_rate = np.random.normal(25, 10)
            usd_rate = np.random.normal(1, 0.3) if year < 2009 else np.random.normal(1, 0.1)
            
            # Calculate yield with various factors
            rainfall_factor = min(1.2, max(0.5, rainfall / 650))
            temp_factor = min(1.1, max(0.6, 1 - abs(temperature - 23) / 10))
            economic_factor = max(0.7, min(1.3, 1 - (inflation_rate - 15) / 100))
            
            # Random events (droughts, good seasons, etc.)
            random_factor = np.random.normal(1, 0.15)
            
            predicted_yield = base_yield * rainfall_factor * temp_factor * economic_factor * random_factor
            
            # Add some noise to actual yield
            actual_yield = predicted_yield * np.random.normal(1, 0.08)
            
            data.append({
                'year': year,
                'rainfall_mm': round(rainfall, 2),
                'temperature_avg': round(temperature, 2),
                'number_of_farmers': farmers,
                'total_hectarage': round(total_hectarage, 2),
                'predicted_yield_kg': round(predicted_yield, 2),
                'actual_yield_kg': round(actual_yield, 2),
                'inflation_rate': round(inflation_rate, 2),
                'interest_rate': round(interest_rate, 2),
                'usd_exchange_rate': round(usd_rate, 4),
                'drought_occurrence': random.choice([0, 1]) if rainfall < 450 else 0,
                'political_stability_index': np.random.normal(50, 20),
                'fertilizer_availability': np.random.normal(80, 15),
                'seed_quality_index': np.random.normal(75, 10)
            })
        
        df = pd.DataFrame(data)
        df.to_csv(os.path.join(output_dir, 'yield_prediction_data.csv'), index=False)
        self.stdout.write('Generated yield prediction data')
    
    def generate_fraud_data(self, output_dir, num_samples):
        """Generate fraud detection training data"""
        self.stdout.write('Generating fraud detection data...')
        
        data = []
        
        # Grade codes and their typical price ranges
        grades = {
            'A1': (4.5, 6.0), 'A2': (4.0, 5.5), 'A3': (3.5, 5.0),
            'L1': (3.8, 5.2), 'L2': (3.3, 4.7), 'L3': (2.8, 4.2),
            'L4': (2.5, 3.8), 'L5': (2.0, 3.3),
            'X1': (2.5, 3.8), 'X2': (2.0, 3.3), 'X3': (1.5, 2.8),
            'X4': (1.2, 2.5), 'X5': (1.0, 2.0),
            'T1': (2.2, 3.5), 'T2': (1.8, 3.0), 'T3': (1.4, 2.5),
            'H1': (1.5, 2.5), 'H2': (1.2, 2.0), 'H3': (1.0, 1.8),
            'C1': (1.8, 2.8), 'C2': (1.5, 2.3),
            'B1': (0.8, 1.5), 'B2': (0.6, 1.2)
        }
        
        locations = ['harare', 'bulawayo', 'mutare', 'gweru', 'chinhoyi']
        seasons = ['peak', 'off_peak']
        
        for i in range(num_samples):
            grade = random.choice(list(grades.keys()))
            min_price, max_price = grades[grade]
            
            # Normal transaction (85% of cases)
            if random.random() < 0.85:
                purchase_price = np.random.normal((min_price + max_price) / 2, 0.3)
                purchase_price = max(min_price * 0.8, purchase_price)
                
                sale_price = purchase_price * np.random.normal(1.15, 0.1)  # Normal markup
                time_difference = max(0.1, np.random.normal(7, 3))  # Days between purchase and sale
                quantity = max(50, np.random.exponential(500))  # kg
                is_fraud = 0
                
            else:  # Fraudulent transactions (15% of cases)
                fraud_type = random.choice(['price_manipulation', 'quick_flip', 'volume_manipulation'])
                
                if fraud_type == 'price_manipulation':
                    purchase_price = max(0.5, np.random.normal(min_price * 0.7, 0.2))  # Buy very low
                    sale_price = purchase_price * np.random.normal(2.5, 0.5)  # Sell very high
                    time_difference = max(0.1, np.random.normal(2, 1))  # Quick turnaround
                    
                elif fraud_type == 'quick_flip':
                    purchase_price = max(min_price * 0.8, np.random.normal((min_price + max_price) / 2, 0.2))
                    sale_price = purchase_price * np.random.normal(1.8, 0.3)  # High markup
                    time_difference = max(0.1, np.random.exponential(1) + 0.5)  # Very quick
                    
                else:  # volume_manipulation
                    purchase_price = max(0.5, np.random.normal(min_price * 0.8, 0.2))
                    sale_price = purchase_price * np.random.normal(1.6, 0.2)
                    time_difference = max(0.1, np.random.normal(5, 2))
                
                quantity = max(20, np.random.exponential(200))  # Smaller quantities for fraud
                is_fraud = 1
            
            # Additional features
            merchant_experience = max(0.1, np.random.exponential(5))  # Years
            market_volatility = max(0.01, np.random.normal(0.15, 0.05))
            season = random.choice(seasons)
            floor_location = random.choice(locations)
            
            # Transaction timing (hour of day) - corrected probabilities
            hour_probabilities = np.array([
                0.01, 0.01, 0.01, 0.01, 0.01, 0.02, 0.03, 0.05,  # 0-7
                0.08, 0.12, 0.15, 0.15, 0.12, 0.08, 0.08, 0.06,  # 8-15
                0.04, 0.03, 0.02, 0.02, 0.01, 0.01, 0.01, 0.01   # 16-23
            ])
            # Normalize probabilities to sum to 1
            hour_probabilities = hour_probabilities / hour_probabilities.sum()
            hour_of_day = np.random.choice(range(24), p=hour_probabilities)
            
            data.append({
                'transaction_id': f'TXN{i:06d}',
                'grade': grade,
                'purchase_price_per_kg': round(max(0.5, purchase_price), 2),
                'sale_price_per_kg': round(max(0.6, sale_price), 2),
                'quantity_kg': round(max(20, quantity), 2),
                'time_difference_days': round(time_difference, 2),
                'price_markup_ratio': round(sale_price / max(0.1, purchase_price), 3),
                'merchant_experience_years': round(merchant_experience, 1),
                'market_volatility': round(market_volatility, 3),
                'season': season,
                'floor_location': floor_location,
                'hour_of_day': hour_of_day,
                'is_fraud': is_fraud
            })
        
        df = pd.DataFrame(data)
        df.to_csv(os.path.join(output_dir, 'fraud_detection_data.csv'), index=False)
        self.stdout.write('Generated fraud detection data')
    
    def generate_side_buying_data(self, output_dir, num_samples):
        """Generate side buying detection data"""
        self.stdout.write('Generating side buying data...')
        
        data = []
        
        for i in range(num_samples):
            farmer_id = f'F{i:05d}'
            merchant_id = f'M{random.randint(1, 200):03d}'
            
            # Contract details
            contracted_quantity = max(500, np.random.normal(2000, 800))  # kg
            contracted_price = max(1.0, np.random.normal(3.5, 0.8))
            
            # Delivery patterns
            if random.random() < 0.7:  # 70% compliant farmers
                delivered_to_contractor = np.random.normal(0.95, 0.1) * contracted_quantity
                delivered_to_contractor = max(0, min(contracted_quantity, delivered_to_contractor))
                delivered_to_others = max(0, np.random.normal(0.05, 0.05) * contracted_quantity)
                is_side_buying = 0
                
            else:  # 30% side buying cases
                delivered_to_contractor = np.random.normal(0.6, 0.2) * contracted_quantity
                delivered_to_contractor = max(0, delivered_to_contractor)
                delivered_to_others = max(0, np.random.normal(0.4, 0.15) * contracted_quantity)
                is_side_buying = 1
            
            # Additional factors
            distance_to_contractor = max(1, np.random.exponential(25))  # km
            distance_to_alternative = max(1, np.random.exponential(15))  # km
            alternative_price_premium = np.random.normal(0.2, 0.1) if is_side_buying else 0
            farmer_debt_level = max(0, np.random.exponential(500))  # USD
            contractor_support_score = max(0, min(100, np.random.normal(75, 20)))  # Out of 100
            
            delivery_ratio = delivered_to_contractor / max(1, contracted_quantity)
            
            data.append({
                'farmer_id': farmer_id,
                'contracted_merchant_id': merchant_id,
                'contracted_quantity_kg': round(contracted_quantity, 2),
                'contracted_price_per_kg': round(contracted_price, 2),
                'delivered_to_contractor_kg': round(delivered_to_contractor, 2),
                'delivered_to_others_kg': round(delivered_to_others, 2),
                'delivery_ratio': round(delivery_ratio, 3),
                'distance_to_contractor_km': round(distance_to_contractor, 1),
                'distance_to_alternative_km': round(distance_to_alternative, 1),
                'alternative_price_premium': round(alternative_price_premium, 3),
                'farmer_debt_level_usd': round(farmer_debt_level, 2),
                'contractor_support_score': round(contractor_support_score, 1),
                'harvest_season': random.choice(['early', 'mid', 'late']),
                'is_side_buying': is_side_buying
            })
        
        df = pd.DataFrame(data)
        df.to_csv(os.path.join(output_dir, 'side_buying_data.csv'), index=False)
        self.stdout.write('Generated side buying data')
    
    def generate_risk_data(self, output_dir, num_samples):
        """Generate risk modeling data"""
        self.stdout.write('Generating risk modeling data...')
        
        # Use the structure from the provided TIMB dataset
        locations = ['Mashonaland West', 'Manicaland', 'Mashonaland Central', 'Masvingo', 'Matabeleland South']
        genders = ['M', 'F']
        merchants = [
            'Tian Ze Tobacco', 'Northern Tobacco (Pvt) Ltd', 'Intercontinental Leaf Tobacco',
            'Zimbabwe Leaf Tobacco (ZLT)', 'Premium Leaf International', 'Onhardt Tobacco (Pvt) Ltd',
            'Premium Leaf Zimbabwe', 'Universal Leaf / ZLT', 'Tobacco Sales Company (TSC)',
            'Cut Rag Processors', 'Shasha Tobacco (Pvt) Ltd', 'Curverid Tobacco (Pvt) Ltd',
            'Mashonaland Tobacco Company (MTC)', 'Aqua Tobacco (Pvt) Ltd'
        ]
        
        grades = [
            'A1', 'A2', 'A3', 'L1', 'L2', 'L3', 'L4', 'L5', 'X1', 'X2', 'X3', 'X4', 'X5',
            'T1', 'T2', 'T3', 'H1', 'H2', 'H3', 'C1', 'C2', 'B1', 'B2'
        ]
        
        data = []
        
        for i in range(num_samples):
            grower_id = f'G{i:05d}'
            location = random.choice(locations)
            gender = random.choice(genders)
            
            # Loan and farming details
            loan_amount = max(100, np.random.lognormal(7.5, 1.2))  # Log-normal distribution for loan amounts
            hectarage = max(0.1, np.random.gamma(2, 2))  # Gamma distribution for land size
            
            # Yields based on location and other factors
            base_yield_per_ha = max(100, np.random.normal(800, 300))
            yields = hectarage * base_yield_per_ha * max(0.1, np.random.normal(1, 0.3))
            
            merchant = random.choice(merchants)
            side_marketer_effect = random.choice([0, 0.1, 0.2, 0.3, 0.5, 0.7, 1.0])
            
            # Calculate derived metrics
            yield_per_ha = yields / max(hectarage, 0.1)
            loan_per_ha = loan_amount / max(hectarage, 0.1)
            
            grade = random.choice(grades)
            mass_produced = yields * np.random.uniform(0.8, 1.2)
            
            # Default probability calculation
            risk_factors = []
            
            # Loan to hectarage ratio risk
            if loan_per_ha > 1000:
                risk_factors.append(0.3)
            elif loan_per_ha > 500:
                risk_factors.append(0.1)
            else:
                risk_factors.append(0.0)
            
            # Yield risk
            if yield_per_ha < 500:
                risk_factors.append(0.4)
            elif yield_per_ha < 800:
                risk_factors.append(0.2)
            else:
                risk_factors.append(0.0)
            
            # Side marketing risk
            if side_marketer_effect > 0.5:
                risk_factors.append(0.3)
            elif side_marketer_effect > 0.3:
                risk_factors.append(0.15)
            else:
                risk_factors.append(0.0)
            
            # Location risk (some areas are riskier)
            location_risk = {
                'Mashonaland West': 0.1,
                'Manicaland': 0.05,
                'Mashonaland Central': 0.08,
                'Masvingo': 0.15,
                'Matabeleland South': 0.25
            }
            risk_factors.append(location_risk[location])
            
            # Calculate default probability
            base_risk = sum(risk_factors)
            default_prob = min(0.99, max(0.01, base_risk + np.random.normal(0, 0.1)))
            default_level = 1 if random.random() < default_prob else 0
            
            data.append({
                'grower_id': grower_id,
                'location': location,
                'gender': gender,
                'loan_amount': round(loan_amount, 2),
                'hectarage': round(hectarage, 2),
                'yields': round(yields, 2),
                'merchant_contractor': merchant,
                'side_marketer_effect': side_marketer_effect,
                'yield_per_ha': round(yield_per_ha, 1),
                'loan_per_ha': round(loan_per_ha, 1),
                'grade_normally_produced': grade,
                'mass_usually_produced_kg': round(mass_produced, 1),
                'default_level': default_level,
                'default_prob': round(default_prob, 6)
            })
        
        df = pd.DataFrame(data)
        df.to_csv(os.path.join(output_dir, 'risk_modeling_data.csv'), index=False)
        self.stdout.write('Generated risk modeling data')