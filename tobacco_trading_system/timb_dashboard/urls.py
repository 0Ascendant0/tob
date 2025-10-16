from django.urls import path
from . import views

app_name = 'timb_dashboard'

urlpatterns = [
    # Main dashboard
    path('', views.dashboard_view, name='dashboard'),
    
    # Transaction management
    path('record-transaction/', views.record_transaction_view, name='record_transaction'),
    path('transactions/', views.TransactionListView.as_view(), name='transaction_list'),
    path('transactions/<str:transaction_id>/', views.TransactionDetailView.as_view(), name='transaction_detail'),
    path('analytics/', views.transaction_analytics_view, name='transaction_analytics'),
    
    # Price management
    path('prices/', views.price_monitoring_view, name='price_monitoring'),
    path('update-daily-prices/', views.update_daily_prices, name='update_daily_prices'),
    path('market/open/', views.open_market, name='open_market'),
    path('market/close/', views.close_market, name='close_market'),
    
    # Floor management
    path('floors/', views.floor_management_view, name='floor_management'),
    
    # Grade management
    path('grades/', views.grade_management_view, name='grade_management'),

    # Merchant management
    path('merchants/', views.merchants_view, name='merchants'),
    path('merchants/create/', views.create_merchant_view, name='create_merchant'),

    # Users management (TIMB admins manage merchant users)
    path('users/', views.users_management_view, name='users'),
    path('users/<int:user_id>/edit/', views.edit_user, name='edit_user'),
    path('users/<int:user_id>/reset-password/', views.reset_user_password, name='reset_user_password'),
    path('users/<int:user_id>/set-password/', views.set_user_password, name='set_user_password'),
    path('users/<int:user_id>/delete/', views.delete_user, name='delete_user'),

    # API endpoints
    path('api/realtime-data/', views.api_realtime_data, name='api_realtime_data'),
]