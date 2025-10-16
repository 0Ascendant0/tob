from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from ai_models.models import AIModel, ModelPerformanceMetric
from decimal import Decimal

User = get_user_model()

class Command(BaseCommand):
    help = 'Initialize AI models in the database'

    def handle(self, *args, **options):
        # Get or create a superuser for model creation
        try:
            admin_user = User.objects.filter(is_superuser=True).first()
            if not admin_user:
                admin_user = User.objects.create_superuser(
                    username='admin',
                    email='admin@example.com',
                    password='admin123'
                )
                self.stdout.write(self.style.SUCCESS('Created admin user'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error creating admin user: {e}'))
            return

        # Create AI models
        models_data = [
            {
                'name': 'Fraud Detection Model',
                'model_type': 'FRAUD_DETECTION',
                'version': '1.0.0',
                'status': 'ACTIVE',
                'accuracy': Decimal('87.5'),
                'precision': Decimal('85.2'),
                'recall': Decimal('89.1'),
                'f1_score': Decimal('87.1'),
                'training_data_size': 10000,
                'description': 'Random Forest classifier for detecting fraudulent transactions'
            },
            {
                'name': 'Yield Prediction Model',
                'model_type': 'YIELD_PREDICTION',
                'version': '1.0.0',
                'status': 'ACTIVE',
                'accuracy': Decimal('92.3'),
                'precision': Decimal('91.8'),
                'recall': Decimal('92.7'),
                'f1_score': Decimal('92.2'),
                'training_data_size': 5000,
                'description': 'Random Forest regressor for predicting tobacco yields'
            },
            {
                'name': 'Side Buying Detection Model',
                'model_type': 'SIDE_BUYING_DETECTION',
                'version': '1.0.0',
                'status': 'ACTIVE',
                'accuracy': Decimal('84.7'),
                'precision': Decimal('82.1'),
                'recall': Decimal('86.3'),
                'f1_score': Decimal('84.1'),
                'training_data_size': 8000,
                'description': 'Random Forest classifier for detecting side buying patterns'
            },
            {
                'name': 'Farmer Risk Assessment Model',
                'model_type': 'RISK_ASSESSMENT',
                'version': '1.0.0',
                'status': 'ACTIVE',
                'accuracy': Decimal('89.2'),
                'precision': Decimal('88.5'),
                'recall': Decimal('89.8'),
                'f1_score': Decimal('89.1'),
                'training_data_size': 12000,
                'description': 'Random Forest classifier for assessing farmer risk'
            }
        ]

        for model_data in models_data:
            model, created = AIModel.objects.get_or_create(
                name=model_data['name'],
                version=model_data['version'],
                defaults={
                    'model_type': model_data['model_type'],
                    'status': model_data['status'],
                    'accuracy': model_data['accuracy'],
                    'precision': model_data['precision'],
                    'recall': model_data['recall'],
                    'f1_score': model_data['f1_score'],
                    'training_data_size': model_data['training_data_size'],
                    'description': model_data['description'],
                    'created_by': admin_user
                }
            )
            
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created {model.name}'))
                
                # Create performance metrics
                ModelPerformanceMetric.objects.create(
                    model=model,
                    metric_name='accuracy',
                    metric_value=model_data['accuracy'],
                    test_data_size=model_data['training_data_size'] // 5,
                    notes='Initial model performance'
                )
            else:
                self.stdout.write(self.style.WARNING(f'{model.name} already exists'))

        self.stdout.write(self.style.SUCCESS('AI models initialization completed!'))
