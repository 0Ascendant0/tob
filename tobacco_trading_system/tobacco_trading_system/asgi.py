import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import realtime_data.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tobacco_trading_system.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            realtime_data.routing.websocket_urlpatterns
        )
    ),
})