import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, mean_absolute_error, classification_report
import joblib
import os
from django.conf import settings
from django.utils import timezone
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

class FraudDetectionModel:
    def __init__(self):
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            class_weight='balanced'
        )
        self.scaler = StandardScaler()
        self.label_encoders = {}
        self.is_trained = False
        self.model_path = os.path.join(settings.BASE_DIR, 'models', 'fraud_detection.joblib')
    
    def prepare_features(self, data):
        """Prepare features for fraud detection"""
        features = data.copy()
        
        # Encode categorical variables
        categorical_cols = ['grade', 'season', 'floor_location']
        for col in categorical_cols:
            if col in features.columns:
                if col not in self.label_encoders:
                    self.label_encoders[col] = LabelEncoder()
                    features[col] = self.label_encoders[col].fit_transform(features[col].astype(str))
                else:
                    features[col] = self.label_encoders[col].transform(features[col].astype(str))
        
        # Feature engineering
        if 'purchase_price_per_kg' in features.columns and 'sale_price_per_kg' in features.columns:
            features['price_markup_ratio'] = features['sale_price_per_kg'] / features['purchase_price_per_kg']
            features['profit_margin'] = features['sale_price_per_kg'] - features['purchase_price_per_kg']
        
        if 'quantity_kg' in features.columns:
            features['log_quantity'] = np.log1p(features['quantity_kg'])
        
        if 'time_difference_days' in features.columns:
            features['is_quick_sale'] = (features['time_difference_days'] < 1).astype(int)
        
        # Select numerical features
        numerical_features = features.select_dtypes(include=[np.number]).columns
        return features[numerical_features]
    
    def train(self, training_data):
        """Train the fraud detection model"""
        print("Training fraud detection model...")
        
        # Prepare features
        X = self.prepare_features(training_data.drop(['is_fraud', 'transaction_id'], axis=1, errors='ignore'))
        y = training_data['is_fraud']
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train model
        self.model.fit(X_train_scaled, y_train)
        
        # Evaluate
        y_pred = self.model.predict(X_test_scaled)
        accuracy = accuracy_score(y_test, y_pred)
        
        print(f"Model accuracy: {accuracy:.4f}")
        print("\nClassification Report:")
        print(classification_report(y_test, y_pred))
        
        self.is_trained = True
        self.save_model()
        
        return {
            'accuracy': accuracy,
            'classification_report': classification_report(y_test, y_pred, output_dict=True)
        }
    
    def predict(self, transaction_data):
        """Predict fraud probability for a transaction"""
        if not self.is_trained:
            self.load_model()
        
        # Prepare features
        X = self.prepare_features(transaction_data)
        X_scaled = self.scaler.transform(X)
        
        # Predict
        fraud_probability = self.model.predict_proba(X_scaled)[:, 1]
        fraud_prediction = self.model.predict(X_scaled)
        
        return {
            'fraud_probability': fraud_probability[0],
            'is_fraud': bool(fraud_prediction[0]),
            'confidence': max(self.model.predict_proba(X_scaled)[0])
        }
    
    def save_model(self):
        """Save trained model"""
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        joblib.dump({
            'model': self.model,
            'scaler': self.scaler,
            'label_encoders': self.label_encoders
        }, self.model_path)
    
    def load_model(self):
        """Load trained model"""
        if os.path.exists(self.model_path):
            model_data = joblib.load(self.model_path)
            self.model = model_data['model']
            self.scaler = model_data['scaler']
            self.label_encoders = model_data['label_encoders']
            self.is_trained = True
            return True
        return False

class YieldPredictionModel:
    def __init__(self):
        self.model = GradientBoostingRegressor(
            n_estimators=200,
            max_depth=8,
            learning_rate=0.1,
            random_state=42
        )
        self.scaler = StandardScaler()
        self.is_trained = False
        self.model_path = os.path.join(settings.BASE_DIR, 'models', 'yield_prediction.joblib')
    
    def prepare_features(self, data):
        """Prepare features for yield prediction"""
        features = data.copy()
        
        # Feature engineering
        features['rainfall_temp_interaction'] = features['rainfall_mm'] * features['temperature_avg']
        features['farmers_per_hectare'] = features['number_of_farmers'] / features['total_hectarage']
        features['economic_stress'] = (features['inflation_rate'] + features['interest_rate']) / 2
        
        # Lag features (previous year's yield if available)
        if 'actual_yield_kg' in features.columns:
            features['prev_yield'] = features['actual_yield_kg'].shift(1)
            features['yield_change'] = features['actual_yield_kg'] - features['prev_yield']
        
        # Weather patterns
        features['drought_risk'] = (features['rainfall_mm'] < 450).astype(int)
        features['optimal_temp'] = ((features['temperature_avg'] >= 20) & 
                                   (features['temperature_avg'] <= 26)).astype(int)
        
        # Remove non-predictive columns
        exclude_cols = ['year', 'actual_yield_kg', 'predicted_yield_kg']
        feature_cols = [col for col in features.columns if col not in exclude_cols]
        
        return features[feature_cols].fillna(features[feature_cols].mean())
    
    def train(self, training_data):
        """Train the yield prediction model"""
        print("Training yield prediction model...")
        
        # Prepare features and target
        X = self.prepare_features(training_data)
        y = training_data['actual_yield_kg']
        
        # Remove rows with missing target values
        mask = ~y.isna()
        X = X[mask]
        y = y[mask]
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train model
        self.model.fit(X_train_scaled, y_train)
        
        # Evaluate
        y_pred = self.model.predict(X_test_scaled)
        mae = mean_absolute_error(y_test, y_pred)
        mape = np.mean(np.abs((y_test - y_pred) / y_test)) * 100
        
        print(f"Model MAE: {mae:.2f}")
        print(f"Model MAPE: {mape:.2f}%")
        
        self.is_trained = True
        self.save_model()
        
        return {
            'mae': mae,
            'mape': mape,
            'feature_importance': dict(zip(X.columns, self.model.feature_importances_))
        }
    
    def predict(self, input_data):
        """Predict yield for given conditions"""
        if not self.is_trained:
            self.load_model()
        
        # Prepare features
        X = self.prepare_features(input_data)
        X_scaled = self.scaler.transform(X)
        
        # Predict
        yield_prediction = self.model.predict(X_scaled)
        
        # Calculate prediction intervals (simple approach)
        prediction_std = np.std(yield_prediction) if len(yield_prediction) > 1 else yield_prediction[0] * 0.1
        
        return {
            'predicted_yield': float(yield_prediction[0]),
            'lower_bound': float(yield_prediction[0] - 1.96 * prediction_std),
            'upper_bound': float(yield_prediction[0] + 1.96 * prediction_std),
            'confidence_interval': 95
        }
    
    def save_model(self):
        """Save trained model"""
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        joblib.dump({
            'model': self.model,
            'scaler': self.scaler
        }, self.model_path)
    
    def load_model(self):
        """Load trained model"""
        if os.path.exists(self.model_path):
            model_data = joblib.load(self.model_path)
            self.model = model_data['model']
            self.scaler = model_data['scaler']
            self.is_trained = True
            return True
        return False

class SideBuyingDetectionModel:
    def __init__(self):
        self.model = RandomForestClassifier(
            n_estimators=150,
            max_depth=12,
            random_state=42,
            class_weight='balanced'
        )
        self.scaler = StandardScaler()
        self.is_trained = False
        self.model_path = os.path.join(settings.BASE_DIR, 'models', 'side_buying.joblib')
    
    def prepare_features(self, data):
        """Prepare features for side buying detection"""
        features = data.copy()
        
        # Feature engineering
        features['delivery_shortfall'] = features['contracted_quantity_kg'] - features['delivered_to_contractor_kg']
        features['side_delivery_ratio'] = features['delivered_to_others_kg'] / features['contracted_quantity_kg']
        features['distance_advantage'] = features['distance_to_contractor_km'] - features['distance_to_alternative_km']
        features['price_incentive'] = features['alternative_price_premium'] * features['contracted_price_per_kg']
        
        # Risk indicators
        features['high_debt'] = (features['farmer_debt_level_usd'] > features['farmer_debt_level_usd'].median()).astype(int)
        features['poor_support'] = (features['contractor_support_score'] < 50).astype(int)
        features['significant_shortfall'] = (features['delivery_ratio'] < 0.8).astype(int)
        
        # Encode categorical
        if 'harvest_season' in features.columns:
            season_map = {'early': 0, 'mid': 1, 'late': 2}
            features['harvest_season'] = features['harvest_season'].map(season_map)
        
        # Select numerical features
        numerical_features = features.select_dtypes(include=[np.number]).columns
        exclude_cols = ['farmer_id', 'contracted_merchant_id', 'is_side_buying']
        feature_cols = [col for col in numerical_features if col not in exclude_cols]
        
        return features[feature_cols].fillna(features[feature_cols].median())
    
    def train(self, training_data):
        """Train the side buying detection model"""
        print("Training side buying detection model...")
        
        # Prepare features
        X = self.prepare_features(training_data)
        y = training_data['is_side_buying']
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train model
        self.model.fit(X_train_scaled, y_train)
        
        # Evaluate
        y_pred = self.model.predict(X_test_scaled)
        accuracy = accuracy_score(y_test, y_pred)
        
        print(f"Model accuracy: {accuracy:.4f}")
        
        self.is_trained = True
        self.save_model()
        
        return {
            'accuracy': accuracy,
            'feature_importance': dict(zip(X.columns, self.model.feature_importances_))
        }
    
    def predict(self, farmer_data):
        """Predict side buying probability"""
        if not self.is_trained:
            self.load_model()
        
        # Prepare features
        X = self.prepare_features(farmer_data)
        X_scaled = self.scaler.transform(X)
        
        # Predict
        side_buying_probability = self.model.predict_proba(X_scaled)[:, 1]
        side_buying_prediction = self.model.predict(X_scaled)
        
        return {
            'side_buying_probability': float(side_buying_probability[0]),
            'is_side_buying': bool(side_buying_prediction[0]),
            'risk_level': 'HIGH' if side_buying_probability[0] > 0.7 else 'MEDIUM' if side_buying_probability[0] > 0.4 else 'LOW'
        }
    
    def save_model(self):
        """Save trained model"""
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        joblib.dump({
            'model': self.model,
            'scaler': self.scaler
        }, self.model_path)
    
    def load_model(self):
        """Load trained model"""
        if os.path.exists(self.model_path):
            model_data = joblib.load(self.model_path)
            self.model = model_data['model']
            self.scaler = model_data['scaler']
            self.is_trained = True
            return True
        return False

# Global model instances
fraud_model = FraudDetectionModel()
yield_model = YieldPredictionModel()
side_buying_model = SideBuyingDetectionModel()

# Helper functions for integration
def get_purchase_recommendations(merchant):
    """Generate AI-powered purchase recommendations for a merchant"""
    from merchant_app.models import PurchaseRecommendation, MerchantInventory
    from timb_dashboard.models import TobaccoGrade
    from realtime_data.models import RealTimePrice
    
    recommendations = []
    
    # Get current inventory
    current_inventory = MerchantInventory.objects.filter(merchant=merchant)
    inventory_grades = {item.grade_id: item.quantity for item in current_inventory}
    
    # Get current market prices
    market_prices = RealTimePrice.objects.all()
    
    for price_data in market_prices:
        grade = price_data.grade
        current_quantity = inventory_grades.get(grade.id, 0)
        
        # Simple recommendation logic (can be enhanced with ML)
        if current_quantity < 100:  # Low stock
            recommended_quantity = 500 - current_quantity
            confidence = 0.8
            reasoning = f"Low inventory for {grade.grade_name}. Current stock: {current_quantity}kg"
            
            # Create recommendation
            recommendation = PurchaseRecommendation.objects.create(
                merchant=merchant,
                grade=grade,
                recommended_quantity=recommended_quantity,
                recommended_price=price_data.current_price,
                confidence_score=confidence,
                reasoning=reasoning
            )
            
            # Set AI analysis
            analysis = {
                'market_trend': 'stable',
                'price_forecast': 'increasing',
                'demand_forecast': 'high',
                'risk_factors': ['market_volatility'],
                'opportunity_score': 0.85
            }
            recommendation.set_ai_analysis(analysis)
            recommendation.save()
            
            recommendations.append(recommendation)
    
    return recommendations

def assess_risk(merchant):
    """Assess various risks for a merchant"""
    from merchant_app.models import RiskAssessment
    from timb_dashboard.models import Transaction
    from django.db.models import Avg, Sum, Count
    
    # Market risk assessment
    recent_transactions = Transaction.objects.filter(
        buyer=merchant.user,
        timestamp__gte=timezone.now() - timedelta(days=30)
    )
    
    if recent_transactions.exists():
        avg_price_volatility = recent_transactions.aggregate(
            volatility=Avg('price_per_kg')
        )['volatility'] or 0
        
        market_risk_score = min(100, (avg_price_volatility / 5.0) * 100)
        
        market_risk = RiskAssessment.objects.create(
            merchant=merchant,
            risk_type='MARKET',
            risk_level='HIGH' if market_risk_score > 70 else 'MEDIUM' if market_risk_score > 40 else 'LOW',
            risk_score=market_risk_score,
            description=f"Market volatility analysis based on recent trading patterns",
        )
        
        mitigation_strategies = [
            "Diversify grade portfolio",
            "Implement hedging strategies",
            "Monitor market trends closely",
            "Maintain flexible purchasing schedules"
        ]
        market_risk.set_mitigation_strategies(mitigation_strategies)
        market_risk.save()
    
    return True