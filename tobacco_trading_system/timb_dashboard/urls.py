from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='timb_dashboard'),
    path('merchants/', views.merchants_view, name='timb_merchants'),
    path('transactions/', views.transactions_view, name='timb_transactions'),
    path('fraud-detection/', views.fraud_detection_view, name='timb_fraud_detection'),
    path('yield-prediction/', views.yield_prediction_view, name='timb_yield_prediction'),
    path('price-monitoring/', views.price_monitoring_view, name='timb_price_monitoring'),
    
    # API endpoints
    path('api/transaction-data/', views.api_transaction_data, name='api_transaction_data'),
    path('api/price-trends/', views.api_price_trends, name='api_price_trends'),
    path('api/secure-report/', views.generate_secure_report, name='api_secure_report'),
]