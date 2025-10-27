# apps/sos/consumers.py

import json
from channels.generic.websocket import AsyncWebsocketConsumer

class DispatcherConsumer(AsyncWebsocketConsumer):
    GROUP_NAME = 'sos_events_dispatchers'

    async def connect(self):
        """
        Вызывается при установлении WebSocket-соединения.
        """
        # Мы будем добавлять в группу только аутентифицированных администраторов
        if self.scope["user"].is_authenticated and self.scope["user"].role == 'ADMIN':
            await self.channel_layer.group_add(
                self.GROUP_NAME,
                self.channel_name
            )
            await self.accept()
        else:
            # Отклоняем соединение для неавторизованных пользователей
            await self.close()

    async def disconnect(self, close_code):
        """
        Вызывается при разрыве WebSocket-соединения.
        """
        await self.channel_layer.group_discard(
            self.GROUP_NAME,
            self.channel_name
        )

    async def receive(self, text_data):
        """
        Вызывается при получении сообщения от клиента (в нашем случае не используется).
        """
        # Мы не ожидаем сообщений от клиентов, только отправляем им
        pass

    async def sos_event_broadcast(self, event):
        """
        Обработчик события, который отправляет данные о SOS-событии клиенту.
        """
        # Отправляем сообщение клиенту через WebSocket
        await self.send(text_data=json.dumps({
            'type': 'sos_event',
            'payload': event['payload']
        }))