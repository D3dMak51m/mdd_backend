# apps/monitoring/views.py
from django.contrib.auth.mixins import UserPassesTestMixin
from django.views.generic import TemplateView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser

from apps.sos.models import SOSEvent


class SentryTestView(APIView):
    """
    Тестовое представление для генерации ошибки и проверки интеграции с Sentry.
    """
    permission_classes = [IsAdminUser]

    def get(self, request, *args, **kwargs):
        # Генерируем ошибку деления на ноль
        result = 1 / 0
        return Response({"result": result}) # Этот код никогда не выполнится


class LiveMonitorView(UserPassesTestMixin, TemplateView):
    template_name = 'admin/monitoring/live_monitor.html'

    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_staff

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Загружаем последние активные события для инициализации карты
        active_events = SOSEvent.objects.filter(
            resolved=False
        ).exclude(
            status=SOSEvent.Status.RESOLVED
        ).order_by('-timestamp')[:50]

        context['active_events'] = active_events
        # Передаем токен (если используем JWT в куках или сессии,
        # но для вебсокетов в браузере админа обычно используется sessionid)
        return context