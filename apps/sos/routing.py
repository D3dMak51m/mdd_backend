# apps/sos/routing.py

from django.urls import re_path
from . import consumers

# Теперь путь не содержит 'ws/', так как он обрабатывается на уровне выше
websocket_urlpatterns = [
    re_path(r'^ws/sos_events/$', consumers.DispatcherConsumer.as_asgi()),
]