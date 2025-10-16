"""
Farmer Risk Assessment Model Export Script
This script exports the trained FarmerRiskModel for use in other systems.
"""

import joblib
import os
import json
from datetime import datetime

class ExportedFarmerRiskModel:
    """
    Standalone version of the FarmerRiskModel for external use.
    This class can be copied to any Python environment.
    """

    def __init__(self, model_path=None):
        """
        Initialize the model.

        Args:
            model_path (str): Path to the saved model file. If None, uses default path.
        """
        self.model = None
        self.scaler = None
        self.label_encoders = {}
        self.is_trained = False
        self.model_path = model_path or 'farmer_risk_model.joblib'

        # Load the model
        self.load_model()

    def load_model(self):
        """Load the trained model from file."""
        try:
            if os.path.exists(self.model_path):
                model_data = joblib.load(self.model_path)
                self.model = model_data['model']
                self.scaler = model_data['scaler']
                self.label_encoders = model_data['label_encoders']
                self.is_trained = model_data['is_trained']
                print(f"Model loaded successfully from {self.model_path}")
            else:
                print(f"Model file not found: {self.model_path}")
        except Exception as e:
            print(f"Error loading model: {e}")

    def predict(self, farmer_data):
        """
        Predict risk for a farmer.

        Args:
            farmer_data (dict): Dictionary containing farmer features:
                - loan_amount (float)
                - hectarage (float)
                - yields (float)
                - yield_per_ha (float)
                - loan_per_ha (float)
                - side_marketer_effect (float)
                - merchant_contractor (str)
                - mass_usually_produced_kg (float)
                - default_prob (float)
                - location (str)
                - gender (str)
                - grade_normally_produced (str)

        Returns:
            dict: Prediction results with risk_score, is_risky, confidence, etc.
        """
        if not self.is_trained:
            return {
                'risk_score': 0.0,
                'is_risky': False,
                'confidence': 0.0,
                'error': 'Model not trained'
            }

        try:
            import pandas as pd
            df = pd.DataFrame([farmer_data])

            # Encode categorical variables
            for feature, encoder in self.label_encoders.items():
                if feature in df.columns:
                    try:
                        df[f'{feature}_encoded'] = encoder.transform(df[feature].astype(str))
                    except ValueError:
                        # Handle unseen categories
                        df[f'{feature}_encoded'] = 0

            # Define features
            features = [
                'loan_amount', 'hectarage', 'yields', 'yield_per_ha', 'loan_per_ha',
                'side_marketer_effect', 'merchant_contractor', 'mass_usually_produced_kg',
                'default_prob', 'location', 'gender', 'grade_normally_produced'
            ]

            # Get final features (original + encoded)
            categorical_features = list(self.label_encoders.keys())
            final_features = [f for f in features if f not in categorical_features]
            final_features += [f'{f}_encoded' for f in categorical_features]

            # Prepare data
            X = df[final_features].fillna(0)
            X_scaled = self.scaler.transform(X)

            # Predict
            if hasattr(self.model, 'predict_proba'):
                risk_probability = self.model.predict_proba(X_scaled)[0][1]
                is_risky = risk_probability > 0.5
                confidence = max(risk_probability, 1 - risk_probability)
            else:
                risk_probability = self.model.predict(X_scaled)[0]
                is_risky = bool(risk_probability)
                confidence = 1.0

            # Determine risk level
            if risk_probability <= 0.3:
                risk_level = 'LOW'
            elif risk_probability <= 0.7:
                risk_level = 'MEDIUM'
            else:
                risk_level = 'HIGH'

            return {
                'risk_score': float(risk_probability),
                'is_risky': is_risky,
                'confidence': float(confidence),
                'risk_level': risk_level,
                'feature_importance': dict(zip(final_features, self.model.feature_importances_))
            }

        except Exception as e:
            print(f"Error predicting farmer risk: {e}")
            return {
                'risk_score': 0.0,
                'is_risky': False,
                'confidence': 0.0,
                'error': str(e)
            }

def export_model(source_path='models/farmer_risk_model.joblib', export_path='exported_farmer_risk_model.joblib'):
    """
    Export the trained model to a new location.

    Args:
        source_path (str): Path to the source model file
        export_path (str): Path where to save the exported model
    """
    try:
        print(f"Attempting to export from: {source_path}")
        print(f"Current working directory: {os.getcwd()}")

        # Ensure source path is absolute
        if not os.path.isabs(source_path):
            source_path = os.path.join(os.getcwd(), source_path)
            print(f"Resolved source path: {source_path}")

        if os.path.exists(source_path):
            print(f"Source file exists: {source_path}")
            # Copy the model file
            import shutil
            export_dir = os.path.dirname(export_path)
            if export_dir:  # Only create directory if export_path has a directory part
                os.makedirs(export_dir, exist_ok=True)
            shutil.copy2(source_path, export_path)
            print(f"Model exported successfully to {export_path}")

            # Create metadata file
            metadata = {
                'exported_at': datetime.now().isoformat(),
                'source': source_path,
                'destination': export_path,
                'model_type': 'FarmerRiskModel',
                'algorithm': 'RandomForestClassifier',
                'usage_instructions': """
To use this model in another system:

1. Install required packages: pip install scikit-learn pandas numpy joblib
2. Copy the ExportedFarmerRiskModel class and the model file
3. Initialize: model = ExportedFarmerRiskModel('path/to/model.joblib')
4. Predict: result = model.predict(farmer_data_dict)
                """
            }

            metadata_path = export_path.replace('.joblib', '_metadata.json')
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)

            print(f"Metadata saved to {metadata_path}")
            return True
        else:
            print(f"Source model not found: {source_path}")
            print("Available files in models directory:")
            models_dir = os.path.join(os.getcwd(), 'models')
            if os.path.exists(models_dir):
                for file in os.listdir(models_dir):
                    print(f"  - {file}")
            return False

    except Exception as e:
        print(f"Error exporting model: {e}")
        import traceback
        traceback.print_exc()
        return False

# Example usage
if __name__ == "__main__":
    # Export the model
    success = export_model()
    if success:
        print("\nModel exported successfully!")
        print("Files created:")
        print("- exported_farmer_risk_model.joblib")
        print("- exported_farmer_risk_model_metadata.json")
        print("\nTo use in another system:")
        print("1. Copy both files to your new project")
        print("2. Use the ExportedFarmerRiskModel class")
        print("3. Call model.predict() with farmer data")
    else:
        print("Failed to export model. Please check if the model file exists.")