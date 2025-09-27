from django.urls import path
from . import views

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='merchant_dashboard'),
    
    # Profile Management
    path('profile/customize/', views.profile_customization, name='merchant_profile_customization'),
    path('dashboard/customize/', views.dashboard_customization, name='merchant_dashboard_customization'),
    
    # Inventory Management
    path('inventory/', views.inventory_management, name='merchant_inventory'),
    path('inventory/add/', views.add_inventory_item, name='merchant_add_inventory'),
    path('inventory/qr-report/', views.generate_qr_report, name='merchant_generate_qr_report'),
    
    # Custom Grades
    path('grades/', views.custom_grades_management, name='merchant_custom_grades'),
    path('grades/create/', views.create_custom_grade, name='merchant_create_custom_grade'),
    
    # Order Management
    path('orders/', views.orders_management, name='merchant_orders'),
    path('orders/create/', views.create_order, name='merchant_create_order'),
    
    # AI Features
    path('ai/recommendations/', views.ai_recommendations, name='merchant_ai_recommendations'),
    path('ai/recommendations/<int:recommendation_id>/implement/', views.implement_recommendation, name='merchant_implement_recommendation'),
    path('farmer-risk/', views.farmer_risk_assessment, name='merchant_farmer_risk_assessment'),
    
    # Inter-Merchant Features
    path('communications/', views.inter_merchant_communications, name='merchant_communications'),
    path('communications/send/', views.send_message, name='merchant_send_message'),
    path('trading/', views.inter_merchant_trading, name='merchant_inter_trading'),
    path('trading/propose/', views.propose_trade, name='merchant_propose_trade'),
    
    # API Endpoints
    path('api/dashboard-data/', views.api_dashboard_data, name='merchant_api_dashboard_data'),
    path('api/price-alerts/', views.api_price_alerts, name='merchant_api_price_alerts'),
]