# mdd_backend/asgi.py

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator # <-- Импорт
import apps.sos.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mdd_backend.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AllowedHostsOriginValidator( # <-- Оборачиваем в валидатор
        AuthMiddlewareStack(
            URLRouter(
                apps.sos.routing.websocket_urlpatterns
            )
        )
    ),
})