from django.urls import path
from . import views

urlpatterns = [
    path('', views.realtime_dashboard, name='realtime_dashboard'),
    path('update-price/', views.update_price, name='update_price'),
    path('create-transaction/', views.create_transaction, name='create_transaction'),
    path('alerts/', views.market_alerts, name='market_alerts'),
    path('alerts/resolve/<int:alert_id>/', views.resolve_alert, name='resolve_alert'),
    path('trading-volume/', views.trading_volume_data, name='trading_volume_data'),
    path('price-trends/', views.price_trends_data, name='price_trends_data'),
]