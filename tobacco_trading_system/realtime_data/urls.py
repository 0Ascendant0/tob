from django.urls import path
from . import views

app_name = 'realtime'

urlpatterns = [
    # Dashboard
    path('', views.realtime_dashboard, name='realtime_dashboard'),
    
    # API Endpoints
    path('api/live-prices/', views.api_live_prices, name='api_live_prices'),
    path('api/live-transactions/', views.api_live_transactions, name='api_live_transactions'),
    path('api/market-analytics/', views.market_analytics, name='api_market_analytics'),
    
    # Real-time Streams
    path('stream/prices/', views.price_stream, name='price_stream'),
    path('stream/transactions/', views.transaction_stream, name='transaction_stream'),
    
    # Market Management
    path('alerts/create/', views.create_market_alert, name='create_market_alert'),
    path('snapshot/generate/', views.generate_market_snapshot, name='generate_market_snapshot'),
]