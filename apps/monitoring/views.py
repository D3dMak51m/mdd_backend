# apps/monitoring/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser

class SentryTestView(APIView):
    """
    Тестовое представление для генерации ошибки и проверки интеграции с Sentry.
    """
    permission_classes = [IsAdminUser]

    def get(self, request, *args, **kwargs):
        # Генерируем ошибку деления на ноль
        result = 1 / 0
        return Response({"result": result}) # Этот код никогда не выполнится