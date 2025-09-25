from django.urls import path
from . import views

urlpatterns = [
    path('', views.model_dashboard, name='ai_models_dashboard'),
    path('train/', views.train_models, name='train_models'),
    path('predict/fraud/', views.predict_fraud, name='predict_fraud'),
    path('predict/yield/', views.predict_yield, name='predict_yield'),
    path('predict/side-buying/', views.predict_side_buying, name='predict_side_buying'),
    path('performance/', views.model_performance, name='model_performance'),
    path('history/', views.prediction_history, name='prediction_history'),
]