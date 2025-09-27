from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/realtime/prices/$', consumers.PriceConsumer.as_asgi()),
    re_path(r'ws/realtime/transactions/$', consumers.TransactionConsumer.as_asgi()),
    re_path(r'ws/realtime/alerts/$', consumers.AlertConsumer.as_asgi()),
    re_path(r'ws/realtime/dashboard/(?P<user_type>\w+)/$', consumers.DashboardConsumer.as_asgi()),
]