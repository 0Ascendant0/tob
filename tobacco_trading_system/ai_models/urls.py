from django.urls import path
from . import views

app_name = 'ai'

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='ai_dashboard'),
    
    # Model Status and Management
    path('status/', views.model_status, name='ai_model_status'),
    path('training-status/', views.training_status, name='ai_training_status'),
    path('retrain/', views.retrain_model, name='ai_retrain_model'),
    
    # AI Predictions
    path('detect-fraud/', views.detect_fraud, name='ai_detect_fraud'),
    path('assess-farmer-risk/', views.assess_farmer_risk, name='ai_assess_farmer_risk'),
    path('predict-yield/', views.predict_yield, name='ai_predict_yield'),
    path('detect-side-buying/', views.detect_side_buying, name='ai_detect_side_buying'),
    
    # Real-time Monitoring
    path('side-buying-monitor/', views.realtime_side_buying_monitor, name='ai_side_buying_monitor'),
]