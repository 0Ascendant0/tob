from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='merchant_dashboard'),
    path('inventory/', views.inventory_view, name='merchant_inventory'),
    path('orders/', views.orders_view, name='merchant_orders'),
    path('orders/create/', views.create_order, name='merchant_create_order'),
    path('custom-grades/', views.custom_grades_view, name='merchant_custom_grades'),
    path('custom-grades/create/', views.create_custom_grade, name='merchant_create_custom_grade'),
    path('recommendations/', views.purchase_recommendations_view, name='merchant_purchase_recommendations'),
    path('risk-management/', views.risk_management_view, name='merchant_risk_management'),
    
    # API endpoints
    path('api/inventory-value/', views.api_inventory_value, name='api_inventory_value'),
    path('api/order-fulfillment/', views.api_order_fulfillment, name='api_order_fulfillment'),
    path('api/inventory-qr/', views.generate_inventory_qr, name='api_inventory_qr'),
]