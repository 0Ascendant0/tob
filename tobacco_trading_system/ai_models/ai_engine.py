import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import accuracy_score, mean_absolute_error
import joblib
import os
from django.conf import settings
from datetime import datetime, timedelta
from django.utils import timezone

class FraudDetectionModel:
    def __init__(self):
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        self.label_encoders = {}
        self.is_trained = False
        self.model_path = os.path.join(settings.BASE_DIR, 'models', 'fraud_model.joblib')
        
        # Load pre-trained model if it exists
        self.load_model()
    
    def train(self, data):
        """Train the fraud detection model"""
        try:
            # Prepare features
            features = [
                'price_markup_ratio', 'quantity_kg', 'time_difference_days',
                'merchant_experience_years', 'market_volatility', 'hour_of_day'
            ]
            
            categorical_features = ['grade', 'season', 'floor_location']
            
            # Encode categorical variables
            for feature in categorical_features:
                if feature in data.columns:
                    le = LabelEncoder()
                    data[f'{feature}_encoded'] = le.fit_transform(data[feature].astype(str))
                    self.label_encoders[feature] = le
                    features.append(f'{feature}_encoded')
            
            X = data[features]
            y = data['is_fraud']
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            
            # Scale features
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            # Train model
            self.model.fit(X_train_scaled, y_train)
            
            # Evaluate
            y_pred = self.model.predict(X_test_scaled)
            accuracy = accuracy_score(y_test, y_pred)
            
            self.is_trained = True
            self.save_model()
            
            return {
                'accuracy': accuracy,
                'training_samples': len(X_train),
                'test_samples': len(X_test)
            }
            
        except Exception as e:
            print(f"Error training fraud detection model: {e}")
            return {'error': str(e)}
    
    def predict(self, transaction_data):
        """Predict fraud probability for a transaction"""
        if not self.is_trained:
            return {
                'fraud_probability': 0.0,
                'is_fraud': False,
                'confidence': 0.0,
                'error': 'Model not trained'
            }
        
        try:
            # Convert transaction to DataFrame
            df = pd.DataFrame([transaction_data])
            
            # Calculate derived features
            df['price_markup_ratio'] = df['sale_price_per_kg'] / df['purchase_price_per_kg']
            df['hour_of_day'] = datetime.now().hour
            
            # Encode categorical variables
            for feature, encoder in self.label_encoders.items():
                if feature in df.columns:
                    try:
                        df[f'{feature}_encoded'] = encoder.transform(df[feature].astype(str))
                    except ValueError:
                        # Handle unseen categories
                        df[f'{feature}_encoded'] = 0
            
            # Prepare features
            features = [
                'price_markup_ratio', 'quantity_kg', 'time_difference_days',
                'merchant_experience_years', 'market_volatility', 'hour_of_day'
            ]
            
            for feature in self.label_encoders.keys():
                features.append(f'{feature}_encoded')
            
            X = df[features].fillna(0)
            X_scaled = self.scaler.transform(X)
            
            # Predict
            fraud_probability = self.model.predict_proba(X_scaled)[0][1]
            is_fraud = fraud_probability > 0.6
            confidence = max(fraud_probability, 1 - fraud_probability)
            
            return {
                'fraud_probability': fraud_probability,
                'is_fraud': is_fraud,
                'confidence': confidence,
                'feature_importance': dict(zip(features, self.model.feature_importances_))
            }
            
        except Exception as e:
            print(f"Error predicting fraud: {e}")
            return {
                'fraud_probability': 0.0,
                'is_fraud': False,
                'confidence': 0.0,
                'error': str(e)
            }
    
    def save_model(self):
        """Save the trained model"""
        try:
            os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
            joblib.dump({
                'model': self.model,
                'scaler': self.scaler,
                'label_encoders': self.label_encoders,
                'is_trained': self.is_trained
            }, self.model_path)
        except Exception as e:
            print(f"Error saving fraud model: {e}")
    
    def load_model(self):
        """Load a pre-trained model"""
        try:
            if os.path.exists(self.model_path):
                model_data = joblib.load(self.model_path)
                self.model = model_data['model']
                self.scaler = model_data['scaler']
                self.label_encoders = model_data['label_encoders']
                self.is_trained = model_data['is_trained']
        except Exception as e:
            print(f"Error loading fraud model: {e}")

class YieldPredictionModel:
    def __init__(self):
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        self.is_trained = False
        self.model_path = os.path.join(settings.BASE_DIR, 'models', 'yield_model.joblib')
        
        # Load pre-trained model if it exists
        self.load_model()
    
    def train(self, data):
        """Train the yield prediction model"""
        try:
            features = [
                'rainfall_mm', 'temperature_avg', 'number_of_farmers',
                'total_hectarage', 'inflation_rate', 'interest_rate',
                'drought_occurrence', 'political_stability_index',
                'fertilizer_availability', 'seed_quality_index'
            ]
            
            X = data[features].fillna(data[features].mean())
            y = data['actual_yield_kg']
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            
            # Scale features
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            # Train model
            self.model.fit(X_train_scaled, y_train)
            
            # Evaluate
            y_pred = self.model.predict(X_test_scaled)
            mae = mean_absolute_error(y_test, y_pred)
            mape = np.mean(np.abs((y_test - y_pred) / y_test)) * 100
            
            self.is_trained = True
            self.save_model()
            
            return {
                'mae': mae,
                'mape': mape,
                'training_samples': len(X_train),
                'test_samples': len(X_test)
            }
            
        except Exception as e:
            print(f"Error training yield prediction model: {e}")
            return {'error': str(e)}
    
    def predict(self, input_data):
        """Predict yield for given conditions"""
        if not self.is_trained:
            return {
                'predicted_yield': 0,
                'confidence_interval': (0, 0),
                'error': 'Model not trained'
            }
        
        try:
            # Convert input to DataFrame
            df = pd.DataFrame([input_data])
            
            features = [
                'rainfall_mm', 'temperature_avg', 'number_of_farmers',
                'total_hectarage', 'inflation_rate', 'interest_rate'
            ]
            
            # Add derived features
            df['drought_occurrence'] = 1 if df['rainfall_mm'].iloc[0] < 400 else 0
            df['political_stability_index'] = input_data.get('political_stability_index', 50)
            df['fertilizer_availability'] = input_data.get('fertilizer_availability', 80)
            df['seed_quality_index'] = input_data.get('seed_quality_index', 75)
            
            features.extend(['drought_occurrence', 'political_stability_index', 
                           'fertilizer_availability', 'seed_quality_index'])
            
            X = df[features].fillna(0)
            X_scaled = self.scaler.transform(X)
            
            # Predict
            predicted_yield = self.model.predict(X_scaled)[0]
            
            # Calculate confidence interval (using standard error)
            predictions = []
            for estimator in self.model.estimators_[:50]:  # Use subset for speed
                pred = estimator.predict(X_scaled)[0]
                predictions.append(pred)
            
            std_error = np.std(predictions)
            confidence_interval = (
                predicted_yield - 1.96 * std_error,
                predicted_yield + 1.96 * std_error
            )
            
            return {
                'predicted_yield': predicted_yield,
                'lower_bound': confidence_interval[0],
                'upper_bound': confidence_interval[1],
                'confidence_interval': confidence_interval,
                'feature_importance': dict(zip(features, self.model.feature_importances_))
            }
            
        except Exception as e:
            print(f"Error predicting yield: {e}")
            return {
                'predicted_yield': 0,
                'confidence_interval': (0, 0),
                'error': str(e)
            }
    
    def save_model(self):
        """Save the trained model"""
        try:
            os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
            joblib.dump({
                'model': self.model,
                'scaler': self.scaler,
                'is_trained': self.is_trained
            }, self.model_path)
        except Exception as e:
            print(f"Error saving yield model: {e}")
    
    def load_model(self):
        """Load a pre-trained model"""
        try:
            if os.path.exists(self.model_path):
                model_data = joblib.load(self.model_path)
                self.model = model_data['model']
                self.scaler = model_data['scaler']
                self.is_trained = model_data['is_trained']
        except Exception as e:
            print(f"Error loading yield model: {e}")

class SideBuyingDetectionModel:
    def __init__(self):
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        self.is_trained = False
        self.model_path = os.path.join(settings.BASE_DIR, 'models', 'side_buying_model.joblib')
        
        # Load pre-trained model if it exists
        self.load_model()
    
    def train(self, data):
        """Train the side buying detection model"""
        try:
            features = [
                'contracted_quantity_kg', 'delivered_to_contractor_kg',
                'delivered_to_others_kg', 'delivery_ratio',
                'distance_to_contractor_km', 'distance_to_alternative_km',
                'alternative_price_premium', 'farmer_debt_level_usd',
                'contractor_support_score'
            ]
            
            # Encode categorical features
            harvest_season_encoded = pd.get_dummies(data['harvest_season'], prefix='season')
            
            X = pd.concat([data[features], harvest_season_encoded], axis=1)
            y = data['is_side_buying']
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            
            # Scale features
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            # Train model
            self.model.fit(X_train_scaled, y_train)
            
            # Evaluate
            y_pred = self.model.predict(X_test_scaled)
            accuracy = accuracy_score(y_test, y_pred)
            
            self.is_trained = True
            self.save_model()
            
            return {
                'accuracy': accuracy,
                'training_samples': len(X_train),
                'test_samples': len(X_test)
            }
            
        except Exception as e:
            print(f"Error training side buying model: {e}")
            return {'error': str(e)}
    
    def predict(self, farmer_data):
        """Predict side buying probability"""
        if not self.is_trained:
            return {
                'is_side_buying': False,
                'confidence': 0.0,
                'error': 'Model not trained'
            }
        
        try:
            # Convert to DataFrame and prepare features
            df = pd.DataFrame([farmer_data])
            
            # Calculate delivery ratio if not provided
            if 'delivery_ratio' not in df.columns:
                df['delivery_ratio'] = df['delivered_to_contractor_kg'] / df['contracted_quantity_kg']
            
            features = [
                'contracted_quantity_kg', 'delivered_to_contractor_kg',
                'delivered_to_others_kg', 'delivery_ratio',
                'distance_to_contractor_km', 'distance_to_alternative_km',
                'alternative_price_premium', 'farmer_debt_level_usd',
                'contractor_support_score'
            ]
            
            # Handle season encoding (simplified)
            season_cols = ['season_early', 'season_mid', 'season_late']
            for col in season_cols:
                df[col] = 0
            
            if 'harvest_season' in farmer_data:
                df[f"season_{farmer_data['harvest_season']}"] = 1
            
            features.extend(season_cols)
            
            X = df[features].fillna(0)
            X_scaled = self.scaler.transform(X)
            
            # Predict
            side_buying_probability = self.model.predict_proba(X_scaled)[0][1]
            is_side_buying = side_buying_probability > 0.5
            confidence = max(side_buying_probability, 1 - side_buying_probability)
            
            return {
                'is_side_buying': is_side_buying,
                'probability': side_buying_probability,
                'confidence': confidence,
                'details': {
                    'delivery_ratio': df['delivery_ratio'].iloc[0],
                    'risk_factors': self._identify_risk_factors(farmer_data)
                }
            }
            
        except Exception as e:
            print(f"Error predicting side buying: {e}")
            return {
                'is_side_buying': False,
                'confidence': 0.0,
                'error': str(e)
            }
    
    def _identify_risk_factors(self, farmer_data):
        """Identify risk factors for side buying"""
        risk_factors = []
        
        delivery_ratio = farmer_data.get('delivered_to_contractor_kg', 0) / farmer_data.get('contracted_quantity_kg', 1)
        
        if delivery_ratio < 0.8:
            risk_factors.append('Low delivery ratio to contractor')
        
        if farmer_data.get('alternative_price_premium', 0) > 0.2:
            risk_factors.append('High alternative price premium')
        
        if farmer_data.get('distance_to_alternative_km', 100) < farmer_data.get('distance_to_contractor_km', 0):
            risk_factors.append('Alternative buyer is closer')
        
        if farmer_data.get('contractor_support_score', 100) < 50:
            risk_factors.append('Low contractor support satisfaction')
        
        return risk_factors
    
    def save_model(self):
        """Save the trained model"""
        try:
            os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
            joblib.dump({
                'model': self.model,
                'scaler': self.scaler,
                'is_trained': self.is_trained
            }, self.model_path)
        except Exception as e:
            print(f"Error saving side buying model: {e}")
    
    def load_model(self):
        """Load a pre-trained model"""
        try:
            if os.path.exists(self.model_path):
                model_data = joblib.load(self.model_path)
                self.model = model_data['model']
                self.scaler = model_data['scaler']
                self.is_trained = model_data['is_trained']
        except Exception as e:
            print(f"Error loading side buying model: {e}")

# Global model instances
fraud_model = FraudDetectionModel()
yield_model = YieldPredictionModel()
side_buying_model = SideBuyingDetectionModel()

# API functions
def detect_fraud(transaction):
    """Detect fraud in a transaction"""
    transaction_data = {
        'grade': transaction.grade.grade_code,
        'purchase_price_per_kg': float(transaction.price_per_kg * 0.9),  # Estimated purchase price
        'sale_price_per_kg': float(transaction.price_per_kg),
        'quantity_kg': float(transaction.quantity),
        'time_difference_days': 1,  # Assume same day for now
        'merchant_experience_years': 5,  # Default value
        'market_volatility': 0.15,  # Default market volatility
        'season': 'peak',
        'floor_location': transaction.floor.location.lower() if transaction.floor else 'unknown'
    }
    
    return fraud_model.predict(transaction_data)

def predict_yield(year, conditions):
    """Predict tobacco yield for given conditions"""
    input_data = {
        'rainfall_mm': conditions.get('rainfall_mm', 650),
        'temperature_avg': conditions.get('temperature_avg', 23.5),
        'number_of_farmers': conditions.get('number_of_farmers', 75000),
        'total_hectarage': conditions.get('total_hectarage', 180000),
        'inflation_rate': conditions.get('inflation_rate', 15),
        'interest_rate': conditions.get('interest_rate', 25),
    }
    
    return yield_model.predict(input_data)

def detect_side_buying(transaction):
    """Detect potential side buying"""
    # This is a simplified implementation
    # In practice, you'd analyze farmer delivery patterns
    
    farmer_data = {
        'contracted_quantity_kg': 1000,  # Default values
        'delivered_to_contractor_kg': float(transaction.quantity),
        'delivered_to_others_kg': 0,
        'distance_to_contractor_km': 20,
        'distance_to_alternative_km': 15,
        'alternative_price_premium': 0.1,
        'farmer_debt_level_usd': 500,
        'contractor_support_score': 70,
        'harvest_season': 'mid'
    }
    
    return side_buying_model.predict(farmer_data)

def get_purchase_recommendations(merchant):
    """Get AI-powered purchase recommendations for a merchant"""
    # This would analyze market conditions, inventory levels, etc.
    # Simplified implementation
    
    recommendations = []
    
    # Analyze current inventory
    from merchant_app.models import MerchantInventory
    
    inventory = MerchantInventory.objects.filter(merchant=merchant)
    low_stock_grades = inventory.filter(quantity__lt=100)
    
    for item in low_stock_grades:
        recommendations.append({
            'type': 'RESTOCK',
            'grade': item.grade.grade_name,
            'current_stock': item.quantity,
            'recommended_quantity': 500,
            'reason': 'Low stock level',
            'confidence': 0.8,
            'estimated_cost': item.grade.base_price * 500,
        })
    
    return recommendations

def assess_risk(merchant):
    """Assess risk for a merchant"""
    # Simplified risk assessment
    risk_factors = []
    risk_score = 0
    
    # Analyze transaction patterns
    from timb_dashboard.models import Transaction
    recent_transactions = Transaction.objects.filter(
        buyer=merchant.user,
        timestamp__gte=timezone.now() - timedelta(days=30)
    )
    
    if recent_transactions.count() == 0:
        risk_factors.append('No recent trading activity')
        risk_score += 0.2
    
    # Check for fraud alerts
    from timb_dashboard.models import FraudAlert
    recent_alerts = FraudAlert.objects.filter(
        merchant=merchant,
        created_at__gte=timezone.now() - timedelta(days=90)
    )
    
    if recent_alerts.count() > 0:
        risk_factors.append(f'{recent_alerts.count()} fraud alerts in last 90 days')
        risk_score += recent_alerts.count() * 0.1
    
    return {
        'risk_score': min(risk_score, 1.0),
        'risk_level': 'HIGH' if risk_score > 0.7 else 'MEDIUM' if risk_score > 0.3 else 'LOW',
        'risk_factors': risk_factors,
        'recommendations': [
            'Increase monitoring of transactions',
            'Review trading patterns',
            'Enhance due diligence procedures'
        ] if risk_score > 0.5 else ['Continue current practices']
    }