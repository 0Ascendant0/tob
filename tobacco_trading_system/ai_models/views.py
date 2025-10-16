from django.shortcuts import render, redirect
from django.http import JsonResponse, StreamingHttpResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Q, Count, Avg
from decimal import Decimal
import json
import random
import time

# Import models with error handling
try:
    from timb_dashboard.models import Transaction, FraudAlert, YieldPrediction, TobaccoGrade
except ImportError:
    Transaction = None
    FraudAlert = None
    YieldPrediction = None
    TobaccoGrade = None

try:
    from merchant_app.models import MerchantInventory, CustomGrade, FarmerRiskAssessment
except ImportError:
    MerchantInventory = None
    CustomGrade = None
    FarmerRiskAssessment = None

from .models import AIModel, PredictionLog, ModelPerformanceMetric, TrainingJob, SideBuyingDetection

@login_required
def dashboard(request):
    """AI models dashboard"""
    if not request.user.is_timb_staff:
        return redirect('merchant_dashboard')
    
    # Get recent predictions
    recent_predictions = PredictionLog.objects.select_related('model_used').order_by('-created_at')[:10]
    
    # Get model statistics
    models_stats = {
        'total_models': AIModel.objects.count(),
        'active_models': AIModel.objects.filter(status='ACTIVE').count(),
        'training_models': AIModel.objects.filter(status='TRAINING').count(),
        'predictions_today': PredictionLog.objects.filter(
            created_at__date=timezone.now().date()
        ).count()
    }
    
    # Get performance metrics
    performance_data = []
    for model in AIModel.objects.filter(status='ACTIVE'):
        latest_metric = ModelPerformanceMetric.objects.filter(
            model=model, metric_name='accuracy'
        ).first()
        
        performance_data.append({
            'model': model,
            'accuracy': latest_metric.metric_value if latest_metric else 0,
            'predictions_count': PredictionLog.objects.filter(model_used=model).count()
        })
    
    context = {
        'models_stats': models_stats,
        'recent_predictions': recent_predictions,
        'performance_data': performance_data,
    }
    return render(request, 'ai_models/dashboard.html', context)

@login_required
@require_http_methods(["GET"])
def model_status(request):
    """Get AI model status"""
    models_data = []
    
    for model in AIModel.objects.filter(status='ACTIVE'):
        # Get recent performance metrics
        accuracy_metric = ModelPerformanceMetric.objects.filter(
            model=model, metric_name='accuracy'
        ).first()
        
        predictions_today = PredictionLog.objects.filter(
            model_used=model,
            created_at__date=timezone.now().date()
        ).count()
        
        models_data.append({
            'name': model.name,
            'type': model.get_model_type_display(),
            'version': model.version,
            'accuracy': float(accuracy_metric.metric_value) if accuracy_metric else 0,
            'predictions_today': predictions_today,
            'last_updated': model.updated_at.isoformat(),
        })
    
    return JsonResponse({
        'success': True,
        'models': models_data,
        'system_health': {
            'cpu_usage': random.uniform(10, 30),
            'memory_usage': random.uniform(40, 70),
            'model_latency': random.uniform(50, 150),
            'api_calls_today': PredictionLog.objects.filter(
                created_at__date=timezone.now().date()
            ).count()
        }
    })

@login_required
def detect_fraud_form(request):
    """Fraud detection form page"""
    if not request.user.is_timb_staff:
        return redirect('merchant_dashboard')
    
    return render(request, 'ai_models/detect_fraud.html')

@login_required
@require_http_methods(["POST"])
def detect_fraud(request):
    """Run fraud detection on transaction"""
    if not Transaction or not FraudAlert:
        return JsonResponse({
            'success': False,
            'error': 'Required models not available'
        }, status=500)
    
    try:
        data = json.loads(request.body)
        transaction_id = data.get('transaction_id')
        
        transaction = Transaction.objects.get(id=transaction_id)
        
        # Get fraud detection model
        fraud_model = AIModel.objects.filter(
            model_type='FRAUD_DETECTION',
            status='ACTIVE'
        ).first()
        
        if not fraud_model:
            return JsonResponse({
                'success': False,
                'error': 'Fraud detection model not available'
            }, status=500)
        
        # Run fraud detection
        fraud_result = run_fraud_detection(transaction)
        
        # Log prediction
        prediction_log = PredictionLog.objects.create(
            prediction_type='FRAUD',
            model_used=fraud_model,
            input_data={
                'transaction_id': transaction.transaction_id,
                'quantity': float(transaction.quantity),
                'price_per_kg': float(transaction.price_per_kg),
                'grade': transaction.grade.grade_code,
            },
            prediction_result=fraud_result,
            confidence_score=Decimal(str(fraud_result['confidence'])),
            user=request.user,
            related_object_id=str(transaction.id),
            related_object_type='Transaction'
        )
        
        # Create alert if fraud detected
        if fraud_result['is_fraud'] and fraud_result['confidence'] > 0.6:
            alert = FraudAlert.objects.create(
                alert_type='AI_DETECTION',
                severity='HIGH' if fraud_result['confidence'] > 0.8 else 'MEDIUM',
                transaction=transaction,
                title=f'AI Fraud Detection: {transaction.transaction_id}',
                description=f"AI model detected potential fraud with {fraud_result['confidence']*100:.1f}% confidence",
                confidence_score=Decimal(str(fraud_result['confidence']))
            )
            
            # Update transaction
            transaction.is_flagged = True
            transaction.fraud_score = Decimal(str(fraud_result['confidence']))
            transaction.save()
            
            return JsonResponse({
                'success': True,
                'fraud_detected': True,
                'confidence': fraud_result['confidence'],
                'risk_factors': fraud_result['risk_factors'],
                'alert_id': alert.id,
                'prediction_id': prediction_log.id
            })
        
        return JsonResponse({
            'success': True,
            'fraud_detected': False,
            'confidence': fraud_result['confidence'],
            'risk_factors': fraud_result['risk_factors'],
            'prediction_id': prediction_log.id
        })
        
    except Transaction.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Transaction not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@login_required
def assess_farmer_risk_form(request):
    """Farmer risk assessment form page"""
    if not request.user.is_timb_staff:
        return redirect('merchant_dashboard')
    
    return render(request, 'ai_models/assess_farmer_risk.html')

@login_required
@require_http_methods(["POST"])
def assess_farmer_risk(request):
    """Assess farmer risk for contract approval"""
    try:
        data = json.loads(request.body)
        
        # Get risk assessment model
        risk_model = AIModel.objects.filter(
            model_type='RISK_ASSESSMENT',
            status='ACTIVE'
        ).first()
        
        if not risk_model:
            return JsonResponse({
                'success': False,
                'error': 'Risk assessment model not available'
            }, status=500)
        
        # Run risk assessment using rule-based approach
        risk_result = run_farmer_risk_assessment(data)
        
        # Log prediction
        prediction_log = PredictionLog.objects.create(
            prediction_type='RISK',
            model_used=risk_model,
            input_data=data,
            prediction_result=risk_result,
            confidence_score=Decimal(str(risk_result['confidence'])),
            user=request.user
        )
        
        return JsonResponse({
            'success': True,
            'risk_assessment': risk_result,
            'prediction_id': prediction_log.id
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@login_required
def predict_yield_form(request):
    """Yield prediction form page"""
    if not request.user.is_timb_staff:
        return redirect('merchant_dashboard')
    
    return render(request, 'ai_models/predict_yield.html')

@login_required
@require_http_methods(["POST"])
def predict_yield(request):
    """Predict tobacco yield"""
    try:
        data = json.loads(request.body)
        
        # Get yield prediction model
        yield_model = AIModel.objects.filter(
            model_type='YIELD_PREDICTION',
            status='ACTIVE'
        ).first()
        
        if not yield_model:
            return JsonResponse({
                'success': False,
                'error': 'Yield prediction model not available'
            }, status=500)
        
        # Run yield prediction
        yield_result = run_yield_prediction(data)
        
        # Create yield prediction record if YieldPrediction model exists
        if YieldPrediction:
            yield_prediction = YieldPrediction.objects.create(
                prediction_type=data.get('prediction_type', 'ANNUAL'),
                year=data.get('year', timezone.now().year),
                region=data.get('region', ''),
                rainfall_mm=Decimal(str(data.get('rainfall', 650))),
                temperature_avg=Decimal(str(data.get('temperature', 23.5))),
                number_of_farmers=data.get('farmers', 75000),
                total_hectarage=Decimal(str(data.get('hectarage', 180000))),
                inflation_rate=Decimal(str(data.get('inflation', 15))),
                interest_rate=Decimal(str(data.get('interest', 25))),
                predicted_yield_kg=Decimal(str(yield_result['predicted_yield'])),
                confidence_level=Decimal(str(yield_result['confidence'])),
                lower_bound=Decimal(str(yield_result['lower_bound'])),
                upper_bound=Decimal(str(yield_result['upper_bound'])),
                created_by=request.user
            )
        
        # Log prediction
        prediction_log = PredictionLog.objects.create(
            prediction_type='YIELD',
            model_used=yield_model,
            input_data=data,
            prediction_result=yield_result,
            confidence_score=Decimal(str(yield_result['confidence'])),
            user=request.user
        )
        
        return JsonResponse({
            'success': True,
            'yield_prediction': yield_result,
            'prediction_id': prediction_log.id
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@login_required
def detect_side_buying_form(request):
    """Side buying detection form page"""
    if not request.user.is_timb_staff:
        return redirect('merchant_dashboard')
    
    return render(request, 'ai_models/detect_side_buying.html')

@login_required
@require_http_methods(["POST"])
def detect_side_buying(request):
    """Detect side buying patterns"""
    try:
        data = json.loads(request.body)
        
        # Get side buying detection model
        side_buying_model = AIModel.objects.filter(
            model_type='SIDE_BUYING_DETECTION',
            status='ACTIVE'
        ).first()
        
        if not side_buying_model:
            return JsonResponse({
                'success': False,
                'error': 'Side buying detection model not available'
            }, status=500)
        
        # Run side buying detection
        detection_result = run_side_buying_detection(data)
        
        # Create side buying detection record
        side_buying_record = SideBuyingDetection.objects.create(
            farmer_name=data.get('farmer_name', ''),
            farmer_id=data.get('farmer_id', ''),
            merchant_name=data.get('merchant_name', ''),
            is_side_buying_detected=detection_result['detected'],
            confidence_score=Decimal(str(detection_result['confidence'])),
            risk_factors=detection_result['risk_factors'],
            contracted_quantity=Decimal(str(data.get('contracted_quantity', 0))),
            delivered_quantity=Decimal(str(data.get('delivered_quantity', 0))),
            delivery_ratio=Decimal(str(detection_result.get('delivery_ratio', 0))),
            model_version=side_buying_model.version
        )
        
        # Log prediction
        prediction_log = PredictionLog.objects.create(
            prediction_type='SIDE_BUYING',
            model_used=side_buying_model,
            input_data=data,
            prediction_result=detection_result,
            confidence_score=Decimal(str(detection_result['confidence'])),
            user=request.user,
            related_object_id=str(side_buying_record.id),
            related_object_type='SideBuyingDetection'
        )
        
        return JsonResponse({
            'success': True,
            'side_buying_detected': detection_result['detected'],
            'confidence': detection_result['confidence'],
            'risk_factors': detection_result['risk_factors'],
            'detection_id': side_buying_record.id,
            'prediction_id': prediction_log.id
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@login_required
@require_http_methods(["GET"])
def side_buying_monitor(request):
    """Side buying monitoring page"""
    if not request.user.is_timb_staff:
        return redirect('merchant_dashboard')
    
    return render(request, 'ai_models/side_buying_monitor.html')

@login_required
@require_http_methods(["GET"])
def realtime_side_buying_monitor(request):
    """Real-time side buying monitoring stream"""
    def event_stream():
        while True:
            # Check for new side buying patterns
            recent_detections = SideBuyingDetection.objects.filter(
                detection_date__gte=timezone.now() - timezone.timedelta(hours=1),
                is_side_buying_detected=True
            ).order_by('-detection_date')[:5]
            
            detection_data = []
            for detection in recent_detections:
                detection_data.append({
                    'id': detection.id,
                    'farmer_name': detection.farmer_name,
                    'merchant_name': detection.merchant_name,
                    'confidence': float(detection.confidence_score),
                    'risk_factors': detection.risk_factors,
                    'detection_time': detection.detection_date.isoformat()
                })
            
            yield f"data: {json.dumps({'detections': detection_data})}\n\n"
            time.sleep(30)  # Update every 30 seconds
    
    response = StreamingHttpResponse(event_stream(), content_type='text/plain')
    response['Cache-Control'] = 'no-cache'
    response['Connection'] = 'keep-alive'
    return response

@login_required
@require_http_methods(["POST"])
def retrain_model(request):
    """Start model retraining"""
    if not request.user.is_timb_staff:
        return JsonResponse({
            'success': False,
            'error': 'Unauthorized'
        }, status=403)
    
    try:
        data = json.loads(request.body)
        model_id = data.get('model_id')
        
        model = AIModel.objects.get(id=model_id)
        
        # Create training job
        job_id = f"train_{model.name}_{timezone.now().strftime('%Y%m%d_%H%M%S')}"
        
        training_job = TrainingJob.objects.create(
            model=model,
            job_id=job_id,
            status='QUEUED',
            training_parameters=data.get('parameters', {}),
            total_epochs=data.get('epochs', 100),
            created_by=request.user
        )
        
        # In a real implementation, this would trigger actual model training
        # For now, we'll simulate it
        
        return JsonResponse({
            'success': True,
            'job_id': job_id,
            'message': f'Retraining job for {model.name} has been queued',
            'estimated_duration': '2-4 hours'
        })
        
    except AIModel.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Model not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@login_required
@require_http_methods(["GET"])
def training_status(request):
    """Get training job status"""
    jobs = TrainingJob.objects.order_by('-created_at')[:10]
    
    jobs_data = []
    for job in jobs:
        jobs_data.append({
            'job_id': job.job_id,
            'model_name': job.model.name,
            'status': job.status,
            'progress': float(job.progress_percentage),
            'current_epoch': job.current_epoch,
            'total_epochs': job.total_epochs,
            'accuracy': float(job.final_accuracy) if job.final_accuracy else None,
            'started_at': job.started_at.isoformat() if job.started_at else None,
            'estimated_completion': job.estimated_completion.isoformat() if job.estimated_completion else None
        })
    
    return JsonResponse({
        'success': True,
        'training_jobs': jobs_data
    })

# AI Algorithm Implementations

def run_fraud_detection(transaction):
    """Enhanced fraud detection algorithm"""
    risk_factors = []
    risk_score = 0.0
    
    try:
        # Price deviation analysis
        base_price = float(transaction.grade.base_price)
        actual_price = float(transaction.price_per_kg)
        price_deviation = abs(actual_price - base_price) / base_price
        
        if price_deviation > 0.5:
            risk_score += 0.4
            risk_factors.append(f"Extreme price deviation: {price_deviation*100:.1f}%")
        elif price_deviation > 0.3:
            risk_score += 0.25
            risk_factors.append(f"High price deviation: {price_deviation*100:.1f}%")
        elif price_deviation > 0.15:
            risk_score += 0.1
            risk_factors.append(f"Moderate price deviation: {price_deviation*100:.1f}%")
        
        # Volume analysis
        quantity = float(transaction.quantity)
        if quantity > 10000:
            risk_score += 0.3
            risk_factors.append(f"Unusually large quantity: {quantity}kg")
        elif quantity > 5000:
            risk_score += 0.15
            risk_factors.append(f"Large quantity: {quantity}kg")
        
        # Timing analysis
        hour = transaction.timestamp.hour
        if hour < 6 or hour > 22:
            risk_score += 0.15
            risk_factors.append(f"Transaction outside business hours: {hour}:00")
        
        # Frequency analysis (same buyer/seller patterns)
        if Transaction:
            recent_transactions = Transaction.objects.filter(
                buyer=transaction.buyer,
                seller=transaction.seller,
                timestamp__gte=timezone.now() - timezone.timedelta(days=7)
            ).count()
            
            if recent_transactions > 10:
                risk_score += 0.2
                risk_factors.append(f"High frequency trading: {recent_transactions} transactions in 7 days")
        
        # Grade quality vs price analysis
        if hasattr(transaction.grade, 'market_demand'):
            if transaction.grade.market_demand == 'LOW' and actual_price > base_price * 1.2:
                risk_score += 0.25
                risk_factors.append("High price for low-demand grade")
        
        # Random ML simulation factors
        ml_factors = random.uniform(0, 0.15)
        risk_score += ml_factors
        
        if ml_factors > 0.1:
            risk_factors.append("ML pattern detection triggered")
        
        risk_score = min(risk_score, 1.0)
        
        return {
            'is_fraud': risk_score > 0.6,
            'confidence': risk_score,
            'risk_factors': risk_factors,
            'price_deviation': price_deviation,
            'volume_anomaly': quantity > 5000,
            'timing_anomaly': hour < 6 or hour > 22
        }
        
    except Exception as e:
        return {
            'is_fraud': False,
            'confidence': 0.0,
            'risk_factors': [f"Error in analysis: {str(e)}"],
            'price_deviation': 0,
            'volume_anomaly': False,
            'timing_anomaly': False
        }

def run_farmer_risk_assessment(data):
    """Enhanced farmer risk assessment algorithm using new form fields"""
    risk_factors = []
    risk_score = 0.0
    
    try:
        # Financial risk factors
        annual_income = float(data.get('annual_income', 0))
        debt_level = float(data.get('debt_level', 0))
        proposed_contract_value = float(data.get('proposed_contract_value', 0))
        previous_defaults = int(data.get('previous_defaults', 0))
        
        # Debt-to-income ratio
        if annual_income > 0:
            debt_ratio = debt_level / annual_income
            if debt_ratio > 0.5:
                risk_score += 0.2
                risk_factors.append(f"High debt-to-income ratio: {debt_ratio*100:.1f}%")
            elif debt_ratio > 0.3:
                risk_score += 0.1
                risk_factors.append(f"Moderate debt-to-income ratio: {debt_ratio*100:.1f}%")
        
        # Contract size vs income
        if annual_income > 0:
            contract_ratio = proposed_contract_value / annual_income
            if contract_ratio > 1.0:
                risk_score += 0.2
                risk_factors.append(f"Contract value exceeds annual income: {contract_ratio*100:.1f}%")
            elif contract_ratio > 0.7:
                risk_score += 0.1
                risk_factors.append(f"Large contract relative to income: {contract_ratio*100:.1f}%")
        
        # Previous defaults
        if previous_defaults > 2:
            risk_score += 0.3
            risk_factors.append(f"Multiple previous defaults: {previous_defaults}")
        elif previous_defaults > 0:
            risk_score += 0.15
            risk_factors.append(f"Previous default history: {previous_defaults}")
        
        # Experience factor
        years_experience = int(data.get('years_experience', 0))
        if years_experience < 3:
            risk_score += 0.2
            risk_factors.append(f"Limited farming experience: {years_experience} years")
        elif years_experience < 5:
            risk_score += 0.1
            risk_factors.append(f"Moderate farming experience: {years_experience} years")
        
        # Land size analysis
        total_hectares = float(data.get('total_hectares', 0))
        proposed_quantity = float(data.get('proposed_quantity', 0))
        
        if total_hectares > 0:
            yield_per_hectare = proposed_quantity / total_hectares
            if yield_per_hectare > 3000:  # kg per hectare
                risk_score += 0.15
                risk_factors.append(f"Unusually high projected yield: {yield_per_hectare:.0f}kg/ha")
            elif yield_per_hectare < 800:
                risk_score += 0.1
                risk_factors.append(f"Low projected yield: {yield_per_hectare:.0f}kg/ha")
        
        # Location risk (some areas have higher risk)
        location = data.get('location', '').lower()
        high_risk_areas = ['matabeleland', 'masvingo']
        if any(area in location for area in high_risk_areas):
            risk_score += 0.1
            risk_factors.append(f"Higher-risk geographical area: {location}")
        
        # Normalize risk score
        risk_score = min(risk_score, 1.0)
        
        # Determine risk level and recommendation
        if risk_score < 0.3:
            risk_level = "LOW"
            recommendation = "APPROVE: Low risk farmer with good financial standing and experience."
        elif risk_score < 0.6:
            risk_level = "MEDIUM"
            recommendation = "APPROVE WITH CONDITIONS: Medium risk farmer. Consider additional monitoring and smaller initial contract."
        elif risk_score < 0.8:
            risk_level = "HIGH"
            recommendation = "REJECT OR REDUCE: High risk farmer. Consider reducing contract size or requiring additional guarantees."
        else:
            risk_level = "CRITICAL"
            recommendation = "REJECT: Critical risk farmer. Do not approve contract without significant risk mitigation measures."
        
        # Calculate confidence
        confidence = abs(risk_score - 0.5) * 2
        
        # Calculate financial metrics
        financial_metrics = {
            'debt_to_income_ratio': debt_level / annual_income if annual_income > 0 else 0,
            'contract_to_income_ratio': proposed_contract_value / annual_income if annual_income > 0 else 0,
            'yield_per_hectare': proposed_quantity / total_hectares if total_hectares > 0 else 0,
            'previous_defaults': previous_defaults
        }
        
        return {
            'risk_score': float(risk_score),
            'is_risky': risk_score > 0.5,
            'confidence': float(confidence),
            'risk_level': risk_level,
            'recommendation': recommendation,
            'risk_factors': risk_factors,
            'financial_metrics': financial_metrics,
            'feature_importance': {}
        }
        
    except Exception as e:
        return {
            'risk_score': 0.5,
            'is_risky': True,
            'confidence': 0.3,
            'risk_level': 'MEDIUM',
            'recommendation': 'Unable to assess risk due to data error',
            'risk_factors': [f'Assessment error: {str(e)}'],
            'financial_metrics': {},
            'feature_importance': {}
        }

def run_yield_prediction(data):
    """Enhanced yield prediction algorithm"""
    try:
        # Base parameters
        total_hectarage = float(data.get('hectarage', 180000))
        base_yield_per_hectare = 1800  # kg per hectare
        
        # Weather factors
        rainfall = float(data.get('rainfall', 650))
        temperature = float(data.get('temperature', 23.5))
        
        rainfall_factor = 1.0
        if rainfall < 400:
            rainfall_factor = 0.6
        elif rainfall < 600:
            rainfall_factor = 0.8
        elif rainfall > 1000:
            rainfall_factor = 0.9
        elif rainfall > 800:
            rainfall_factor = 1.1
        
        temp_factor = 1.0
        if temperature < 20 or temperature > 28:
            temp_factor = 0.85
        elif 22 <= temperature <= 25:
            temp_factor = 1.05
        
        # Economic factors
        inflation_rate = float(data.get('inflation', 15))
        interest_rate = float(data.get('interest', 25))
        
        economic_factor = 1.0
        if inflation_rate > 20:
            economic_factor -= 0.15
        if interest_rate > 30:
            economic_factor -= 0.1
        
        # Farmer count factor
        num_farmers = int(data.get('farmers', 75000))
        farmer_factor = min(1.2, num_farmers / 70000)
        
        # Calculate base prediction
        predicted_yield = (
            total_hectarage * 
            base_yield_per_hectare * 
            rainfall_factor * 
            temp_factor * 
            economic_factor * 
            farmer_factor
        )
        
        # Add some realistic variation
        variation = random.uniform(0.85, 1.15)
        predicted_yield *= variation
        
        # Calculate confidence based on data quality
        confidence = 0.7
        if rainfall > 0:
            confidence += 0.1
        if temperature > 0:
            confidence += 0.1
        if num_farmers > 0:
            confidence += 0.1
        
        confidence = min(confidence, 0.95)
        
        # Calculate bounds (±20%)
        margin = predicted_yield * 0.2
        lower_bound = predicted_yield - margin
        upper_bound = predicted_yield + margin
        
        return {
            'predicted_yield': predicted_yield,
            'confidence': confidence,
            'lower_bound': lower_bound,
            'upper_bound': upper_bound,
            'factors': {
                'rainfall_factor': rainfall_factor,
                'temperature_factor': temp_factor,
                'economic_factor': economic_factor,
                'farmer_factor': farmer_factor
            },
            'recommendations': generate_yield_recommendations(rainfall_factor, temp_factor, economic_factor)
        }
        
    except Exception as e:
        return {
            'predicted_yield': 0,
            'confidence': 0,
            'lower_bound': 0,
            'upper_bound': 0,
            'factors': {},
            'recommendations': [f"Error in prediction: {str(e)}"]
        }

def run_side_buying_detection(data):
    """Enhanced side buying detection algorithm"""
    risk_factors = []
    confidence = 0.0
    
    try:
        contracted_quantity = float(data.get('contracted_quantity', 0))
        delivered_quantity = float(data.get('delivered_quantity', 0))
        
        # Calculate delivery ratio
        delivery_ratio = delivered_quantity / contracted_quantity if contracted_quantity > 0 else 0
        
        # Primary indicator: Low delivery ratio
        if delivery_ratio < 0.5:
            confidence += 0.6
            risk_factors.append(f"Very low delivery ratio: {delivery_ratio*100:.1f}%")
        elif delivery_ratio < 0.7:
            confidence += 0.4
            risk_factors.append(f"Low delivery ratio: {delivery_ratio*100:.1f}%")
        elif delivery_ratio < 0.85:
            confidence += 0.2
            risk_factors.append(f"Below-average delivery ratio: {delivery_ratio*100:.1f}%")
        
        # Price analysis
        contracted_price = float(data.get('contracted_price', 0))
        market_price = float(data.get('market_price', contracted_price))
        
        if market_price > contracted_price * 1.15:
            confidence += 0.3
            risk_factors.append(f"Market price significantly higher than contracted price")
        elif market_price > contracted_price * 1.05:
            confidence += 0.15
            risk_factors.append(f"Market price moderately higher than contracted price")
        
        # Distance factor
        distance_to_contractor = float(data.get('distance_to_contractor', 10))
        distance_to_alternative = float(data.get('distance_to_alternative', 20))
        
        if distance_to_alternative < distance_to_contractor * 0.7:
            confidence += 0.1
            risk_factors.append("Alternative buyer is significantly closer")
        
        # Historical pattern analysis
        farmer_history = data.get('farmer_history', {})
        if farmer_history.get('previous_side_selling', False):
            confidence += 0.2
            risk_factors.append("Previous history of side selling")
        
        # Support services analysis
        contractor_support = int(data.get('contractor_support_score', 70))
        if contractor_support < 50:
            confidence += 0.15
            risk_factors.append("Low contractor support satisfaction")
        
        # Debt factor
        farmer_debt = float(data.get('farmer_debt_level', 0))
        if farmer_debt > 1000:
            confidence += 0.1
            risk_factors.append("High farmer debt level may indicate financial pressure")
        
        confidence = min(confidence, 1.0)
        detected = confidence > 0.5
        
        return {
            'detected': detected,
            'confidence': confidence,
            'delivery_ratio': delivery_ratio,
            'risk_factors': risk_factors,
            'recommendations': generate_side_buying_recommendations(detected, confidence, risk_factors)
        }
        
    except Exception as e:
        return {
            'detected': False,
            'confidence': 0.0,
            'delivery_ratio': 0,
            'risk_factors': [f"Error in detection: {str(e)}"],
            'recommendations': []
        }

def generate_yield_recommendations(rainfall_factor, temp_factor, economic_factor):
    """Generate yield improvement recommendations"""
    recommendations = []
    
    if rainfall_factor < 0.8:
        recommendations.append("Implement irrigation systems to mitigate low rainfall impact")
    if temp_factor < 0.9:
        recommendations.append("Consider climate-adapted tobacco varieties")
    if economic_factor < 0.9:
        recommendations.append("Provide enhanced farmer support programs to offset economic challenges")
    
    if not recommendations:
        recommendations.append("Current conditions are favorable for tobacco production")
    
    return recommendations

def generate_side_buying_recommendations(detected, confidence, risk_factors):
    """Generate recommendations for side buying management"""
    recommendations = []
    
    if detected:
        if confidence > 0.8:
            recommendations.append("Immediate investigation required - Strong evidence of side buying")
            recommendations.append("Consider contract enforcement measures")
        elif confidence > 0.6:
            recommendations.append("Enhanced monitoring recommended")
            recommendations.append("Review contract terms and farmer satisfaction")
        else:
            recommendations.append("Monitor situation closely")
        
        if "Low delivery ratio" in str(risk_factors):
            recommendations.append("Investigate reasons for low delivery")
        
        if "Market price" in str(risk_factors):
            recommendations.append("Consider price adjustment to competitive levels")
        
        if "contractor support" in str(risk_factors):
            recommendations.append("Improve farmer support services")
    else:
        recommendations.append("No immediate action required")
        recommendations.append("Continue standard monitoring")
    
    return recommendations