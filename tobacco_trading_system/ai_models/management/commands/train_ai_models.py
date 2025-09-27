from django.core.management.base import BaseCommand
from ai_models.ai_engine import fraud_model, yield_model, side_buying_model
import pandas as pd
import os
from django.conf import settings

class Command(BaseCommand):
    help = 'Train AI models with latest data'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--model',
            choices=['fraud', 'yield', 'side_buying', 'all'],
            default='all',
            help='Which model to train',
        )
        parser.add_argument(
            '--data-path',
            type=str,
            help='Path to training data directory',
            default=os.path.join(settings.BASE_DIR, 'data')
        )
    
    def handle(self, *args, **options):
        model_type = options['model']
        data_path = options['data_path']
        
        if model_type in ['fraud', 'all']:
            self.train_fraud_model(data_path)
        
        if model_type in ['yield', 'all']:
            self.train_yield_model(data_path)
        
        if model_type in ['side_buying', 'all']:
            self.train_side_buying_model(data_path)
        
        self.stdout.write(
            self.style.SUCCESS('Model training completed successfully')
        )
    
    def train_fraud_model(self, data_path):
        """Train fraud detection model"""
        self.stdout.write('Training fraud detection model...')
        
        try:
            # Load fraud detection data
            fraud_data_path = os.path.join(data_path, 'fraud_detection_data.csv')
            if not os.path.exists(fraud_data_path):
                self.stdout.write(
                    self.style.WARNING('Fraud data not found. Run generate_synthetic_data first.')
                )
                return
            
            data = pd.read_csv(fraud_data_path)
            
            # Train the model
            results = fraud_model.train(data)
            
            if 'error' in results:
                self.stdout.write(
                    self.style.ERROR(f'Fraud model training failed: {results["error"]}')
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Fraud model trained - Accuracy: {results["accuracy"]:.3f}, '
                        f'Training samples: {results["training_samples"]}'
                    )
                )
        
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error training fraud model: {str(e)}')
            )
    
    def train_yield_model(self, data_path):
        """Train yield prediction model"""
        self.stdout.write('Training yield prediction model...')
        
        try:
            # Load yield data
            yield_data_path = os.path.join(data_path, 'yield_prediction_data.csv')
            if not os.path.exists(yield_data_path):
                self.stdout.write(
                    self.style.WARNING('Yield data not found. Run generate_synthetic_data first.')
                )
                return
            
            data = pd.read_csv(yield_data_path)
            
            # Train the model
            results = yield_model.train(data)
            
            if 'error' in results:
                self.stdout.write(
                    self.style.ERROR(f'Yield model training failed: {results["error"]}')
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Yield model trained - MAE: {results["mae"]:.2f}, '
                        f'MAPE: {results["mape"]:.2f}%'
                    )
                )
        
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error training yield model: {str(e)}')
            )
    
    def train_side_buying_model(self, data_path):
        """Train side buying detection model"""
        self.stdout.write('Training side buying detection model...')
        
        try:
            # Load side buying data
            side_buying_data_path = os.path.join(data_path, 'side_buying_data.csv')
            if not os.path.exists(side_buying_data_path):
                self.stdout.write(
                    self.style.WARNING('Side buying data not found. Run generate_synthetic_data first.')
                )
                return
            
            data = pd.read_csv(side_buying_data_path)
            
            # Train the model
            results = side_buying_model.train(data)
            
            if 'error' in results:
                self.stdout.write(
                    self.style.ERROR(f'Side buying model training failed: {results["error"]}')
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Side buying model trained - Accuracy: {results["accuracy"]:.3f}, '
                        f'Training samples: {results["training_samples"]}'
                    )
                )
        
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error training side buying model: {str(e)}')
            )