# mdd_backend/asgi.py

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import apps.sos.routing # Предполагаемый файл для WebSocket роутинга

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mdd_backend.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            apps.sos.routing.websocket_urlpatterns
        )
    ),
})