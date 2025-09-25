from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/realtime/$', consumers.RealtimeDataConsumer.as_asgi()),
    re_path(r'ws/merchant/$', consumers.MerchantDataConsumer.as_asgi()),
]