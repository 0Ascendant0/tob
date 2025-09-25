from django.core.management.base import BaseCommand
from django.conf import settings
from ai_models.ai_engine import fraud_model, yield_model, side_buying_model
import pandas as pd
import os

class Command(BaseCommand):
    help = 'Train AI models with synthetic data'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--model',
            type=str,
            choices=['fraud', 'yield', 'side_buying', 'all'],
            default='all',
            help='Which model to train'
        )
    
    def handle(self, *args, **options):
        data_dir = os.path.join(settings.BASE_DIR, 'data')
        
        if not os.path.exists(data_dir):
            self.stdout.write(
                self.style.ERROR('Data directory not found. Run generate_synthetic_data first.')
            )
            return
        
        model_type = options['model']
        
        if model_type in ['fraud', 'all']:
            self.train_fraud_model(data_dir)
        
        if model_type in ['yield', 'all']:
            self.train_yield_model(data_dir)
        
        if model_type in ['side_buying', 'all']:
            self.train_side_buying_model(data_dir)
        
        self.stdout.write(
            self.style.SUCCESS('Model training completed')
        )
    
    def train_fraud_model(self, data_dir):
        """Train fraud detection model"""
        fraud_data_path = os.path.join(data_dir, 'fraud_detection_data.csv')
        
        if not os.path.exists(fraud_data_path):
            self.stdout.write(
                self.style.WARNING('Fraud detection data not found')
            )
            return
        
        self.stdout.write('Training fraud detection model...')
        
        fraud_data = pd.read_csv(fraud_data_path)
        results = fraud_model.train(fraud_data)
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Fraud model trained - Accuracy: {results["accuracy"]:.4f}'
            )
        )
    
    def train_yield_model(self, data_dir):
        """Train yield prediction model"""
        yield_data_path = os.path.join(data_dir, 'yield_prediction_data.csv')
        
        if not os.path.exists(yield_data_path):
            self.stdout.write(
                self.style.WARNING('Yield prediction data not found')
            )
            return
        
        self.stdout.write('Training yield prediction model...')
        
        yield_data = pd.read_csv(yield_data_path)
        results = yield_model.train(yield_data)
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Yield model trained - MAE: {results["mae"]:.2f}, MAPE: {results["mape"]:.2f}%'
            )
        )
    
    def train_side_buying_model(self, data_dir):
        """Train side buying detection model"""
        side_buying_data_path = os.path.join(data_dir, 'side_buying_data.csv')
        
        if not os.path.exists(side_buying_data_path):
            self.stdout.write(
                self.style.WARNING('Side buying data not found')
            )
            return
        
        self.stdout.write('Training side buying detection model...')
        
        side_buying_data = pd.read_csv(side_buying_data_path)
        results = side_buying_model.train(side_buying_data)
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Side buying model trained - Accuracy: {results["accuracy"]:.4f}'
            )
        )