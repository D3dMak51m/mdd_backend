# mdd_backend/asgi.py

import os
from django.core.asgi import get_asgi_application

# 1. Устанавливаем настройки
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mdd_backend.settings')

# 2. Инициализируем Django (это загрузит приложения и модели)
# Важно сделать это ДО импорта роутинга и консьюмеров!
django_asgi_app = get_asgi_application()

# 3. Теперь можно безопасно импортировать компоненты Channels
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator
import apps.sos.routing

application = ProtocolTypeRouter({
    # Django's ASGI application to handle traditional HTTP requests
    "http": django_asgi_app,

    # WebSocket handler
    "websocket": AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter(
                apps.sos.routing.websocket_urlpatterns
            )
        )
    ),
})