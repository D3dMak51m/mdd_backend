# mdd_backend/middleware.py (исправленная версия)

from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import AccessToken
from urllib.parse import parse_qs

User = get_user_model()


@database_sync_to_async
def get_user(token_key):
    try:
        access_token = AccessToken(token_key)
        user_id = access_token['user_id']
        return User.objects.get(id=user_id)
    except Exception:
        return None


class JwtAuthMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        query_string = scope.get('query_string', b'').decode()
        query_params = parse_qs(query_string)
        token = query_params.get('token', [None])[0]

        if not token:
            headers = dict(scope['headers'])
            auth_header = headers.get(b'authorization', b'').decode()
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]

        user = await get_user(token) if token else None

        if user:
            scope['user'] = user
        else:
            # ИМПОРТИРУЕМ ЗДЕСЬ, А НЕ В НАЧАЛЕ ФАЙЛА
            from django.contrib.auth.models import AnonymousUser
            scope['user'] = AnonymousUser()

        return await self.app(scope, receive, send)