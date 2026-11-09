# apps/sos/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.core.cache import cache
from asgiref.sync import sync_to_async
from apps.users.models import User


class DispatcherConsumer(AsyncWebsocketConsumer):
    GROUP_NAME = 'sos_events_dispatchers'
    ONLINE_USERS_KEY = 'online_dispatchers_set'

    async def connect(self):
        self.user = self.scope["user"]

        if self.user.is_authenticated and (self.user.role == 'ADMIN' or self.user.is_staff):
            await self.channel_layer.group_add(self.GROUP_NAME, self.channel_name)
            await self.accept()

            # Добавляем пользователя в список онлайн
            await self.add_user_to_online(self.user.id)
            # Рассылаем всем обновленный список
            await self.broadcast_online_users()
        else:
            await self.close()

    async def disconnect(self, close_code):
        if hasattr(self, 'user') and self.user.is_authenticated:
            await self.channel_layer.group_discard(self.GROUP_NAME, self.channel_name)
            # Удаляем пользователя
            await self.remove_user_from_online(self.user.id)
            await self.broadcast_online_users()

    async def receive(self, text_data):
        pass

    # --- Handlers for messages from channel layer ---

    async def sos_event_broadcast(self, event):
        """Отправка нового инцидента"""
        await self.send(text_data=json.dumps({
            'type': 'sos_event',
            'payload': event['payload']
        }))

    async def online_users_update(self, event):
        """Отправка списка онлайн пользователей"""
        await self.send(text_data=json.dumps({
            'type': 'online_users',
            'payload': event['payload']
        }))

    # --- Helpers ---

    @sync_to_async
    def add_user_to_online(self, user_id):
        # Используем Redis Set для хранения уникальных ID
        # В реальном проекте лучше использовать django-redis connection напрямую,
        # но через cache тоже можно, если настроен Redis backend.
        # Внимание: cache.set не подходит для множеств, нужен raw redis или эмуляция.
        # Для простоты используем список в кэше с небольшим TTL

        # Вариант для production: channel_layer.group_channels (но это сложно получить)
        # Простой вариант:
        current_users = cache.get(self.ONLINE_USERS_KEY, set())
        current_users.add(user_id)
        cache.set(self.ONLINE_USERS_KEY, current_users, timeout=86400)

    @sync_to_async
    def remove_user_from_online(self, user_id):
        current_users = cache.get(self.ONLINE_USERS_KEY, set())
        if user_id in current_users:
            current_users.remove(user_id)
            cache.set(self.ONLINE_USERS_KEY, current_users, timeout=86400)

    @sync_to_async
    def get_online_users_data(self):
        user_ids = cache.get(self.ONLINE_USERS_KEY, set())
        users = User.objects.filter(id__in=user_ids).values('id', 'full_name', 'email')
        return list(users)

    async def broadcast_online_users(self):
        users_data = await self.get_online_users_data()
        await self.channel_layer.group_send(
            self.GROUP_NAME,
            {
                'type': 'online_users_update',
                'payload': users_data
            }
        )