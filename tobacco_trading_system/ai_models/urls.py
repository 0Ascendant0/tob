from django.urls import path
from . import views

app_name = 'ai_models'

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # Model status and monitoring
    path('model-status/', views.model_status, name='model_status'),
    path('training-status/', views.training_status, name='training_status'),
    
    # Prediction endpoints
    path('detect-fraud/', views.detect_fraud_form, name='detect_fraud'),
    path('detect-fraud/api/', views.detect_fraud, name='detect_fraud_api'),
    path('assess-farmer-risk/', views.assess_farmer_risk_form, name='assess_farmer_risk'),
    path('assess-farmer-risk/api/', views.assess_farmer_risk, name='assess_farmer_risk_api'),
    path('predict-yield/', views.predict_yield_form, name='predict_yield'),
    path('predict-yield/api/', views.predict_yield, name='predict_yield_api'),
    path('detect-side-buying/', views.detect_side_buying_form, name='detect_side_buying'),
    path('detect-side-buying/api/', views.detect_side_buying, name='detect_side_buying_api'),
    
    # Training endpoints
    path('retrain-model/', views.retrain_model, name='retrain_model'),
    
    # Real-time monitoring
    path('realtime-side-buying-monitor/', views.realtime_side_buying_monitor, name='realtime_side_buying_monitor'),
    path('side-buying-monitor/', views.side_buying_monitor, name='side_buying_monitor'),
]