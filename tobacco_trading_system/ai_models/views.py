from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.utils import timezone
from .models import YieldPredictionData, PredictionLog, ModelPerformanceMetric
from .ai_engine import fraud_model, yield_model, side_buying_model
import pandas as pd
import json
import os
from django.conf import settings

@login_required
def model_dashboard(request):
    """AI Models dashboard"""
    # Model performance metrics
    latest_metrics = ModelPerformanceMetric.objects.values('model_name').distinct()
    
    # Recent predictions
    recent_predictions = PredictionLog.objects.order_by('-created_at')[:20]
    
    # Yield prediction data
    yield_predictions = YieldPredictionData.objects.order_by('-year')[:10]
    
    context = {
        'latest_metrics': latest_metrics,
        'recent_predictions': recent_predictions,
        'yield_predictions': yield_predictions,
    }
    
    return render(request, 'ai_models/dashboard.html', context)

@csrf_exempt
@login_required
def train_models(request):
    """Train AI models with synthetic data"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST method required'}, status=405)
    
    results = {}
    data_dir = os.path.join(settings.BASE_DIR, 'data')
    
    try:
        # Train fraud detection model
        fraud_data_path = os.path.join(data_dir, 'fraud_detection_data.csv')
        if os.path.exists(fraud_data_path):
            fraud_data = pd.read_csv(fraud_data_path)
            fraud_results = fraud_model.train(fraud_data)
            results['fraud_detection'] = fraud_results
        
        # Train yield prediction model
        yield_data_path = os.path.join(data_dir, 'yield_prediction_data.csv')
        if os.path.exists(yield_data_path):
            yield_data = pd.read_csv(yield_data_path)
            yield_results = yield_model.train(yield_data)
            results['yield_prediction'] = yield_results
        
        # Train side buying detection model
        side_buying_data_path = os.path.join(data_dir, 'side_buying_data.csv')
        if os.path.exists(side_buying_data_path):
            side_buying_data = pd.read_csv(side_buying_data_path)
            side_buying_results = side_buying_model.train(side_buying_data)
            results['side_buying_detection'] = side_buying_results
        
        # Log training results
        PredictionLog.objects.create(
            prediction_type='MODEL_TRAINING',
            model_used='ALL_MODELS',
            input_data={'training_initiated_by': request.user.username},
            prediction_result=results,
            confidence_score=1.0,
            created_by=request.user
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Models trained successfully',
            'results': results
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@csrf_exempt
@login_required
def predict_fraud(request):
    """Predict fraud for a transaction"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST method required'}, status=405)
    
    try:
        data = json.loads(request.body)
        
        # Convert to DataFrame
        transaction_df = pd.DataFrame([data])
        
        # Make prediction
        prediction = fraud_model.predict(transaction_df)
        
        # Log prediction
        PredictionLog.objects.create(
            prediction_type='FRAUD',
            model_used='RandomForestClassifier',
            input_data=data,
            prediction_result=prediction,
            confidence_score=prediction['confidence'],
            created_by=request.user
        )
        
        return JsonResponse({
            'success': True,
            'prediction': prediction
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@csrf_exempt
@login_required
def predict_yield(request):
    """Predict tobacco yield"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST method required'}, status=405)
    
    try:
        data = json.loads(request.body)
        
        # Convert to DataFrame
        input_df = pd.DataFrame([data])
        
        # Make prediction
        prediction = yield_model.predict(input_df)
        
        # Log prediction
        PredictionLog.objects.create(
            prediction_type='YIELD',
            model_used='GradientBoostingRegressor',
            input_data=data,
            prediction_result=prediction,
            confidence_score=0.9,  # Default confidence for regression
            created_by=request.user
        )
        
        return JsonResponse({
            'success': True,
            'prediction': prediction
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@csrf_exempt
@login_required
def predict_side_buying(request):
    """Predict side buying risk for a farmer"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST method required'}, status=405)
    
    try:
        data = json.loads(request.body)
        
        # Convert to DataFrame
        farmer_df = pd.DataFrame([data])
        
        # Make prediction
        prediction = side_buying_model.predict(farmer_df)
        
        # Log prediction
        PredictionLog.objects.create(
            prediction_type='SIDE_BUYING',
            model_used='RandomForestClassifier',
            input_data=data,
            prediction_result=prediction,
            confidence_score=prediction.get('side_buying_probability', 0.5),
            created_by=request.user
        )
        
        return JsonResponse({
            'success': True,
            'prediction': prediction
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@login_required
def model_performance(request):
    """View model performance metrics"""
    model_name = request.GET.get('model', 'all')
    
    if model_name != 'all':
        metrics = ModelPerformanceMetric.objects.filter(model_name=model_name)
    else:
        metrics = ModelPerformanceMetric.objects.all()
    
    metrics = metrics.order_by('-measurement_date')[:50]
    
    return JsonResponse({
        'metrics': [
            {
                'model_name': metric.model_name,
                'metric_name': metric.metric_name,
                'metric_value': metric.metric_value,
                'measurement_date': metric.measurement_date.isoformat(),
            }
            for metric in metrics
        ]
    })

@login_required
def prediction_history(request):
    """View prediction history"""
    prediction_type = request.GET.get('type', 'all')
    limit = int(request.GET.get('limit', 50))
    
    query = PredictionLog.objects.all()
    
    if prediction_type != 'all':
        query = query.filter(prediction_type=prediction_type)
    
    predictions = query.order_by('-created_at')[:limit]
    
    return JsonResponse({
        'predictions': [
            {
                'id': pred.id,
                'prediction_type': pred.prediction_type,
                'model_used': pred.model_used,
                'confidence_score': pred.confidence_score,
                'created_at': pred.created_at.isoformat(),
                'created_by': pred.created_by.username if pred.created_by else None,
            }
            for pred in predictions
        ]
    })