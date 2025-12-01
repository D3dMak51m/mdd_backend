# mdd_backend/urls.py (ОКОНЧАТЕЛЬНО ИСПРАВЛЕННАЯ ВЕРСИЯ)

from django.contrib import admin
from django.urls import path, include
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
from django_prometheus.exports import ExportToDjangoView  # Импорт остается

from apps.monitoring.views import LiveMonitorView

schema_view = get_schema_view(
    openapi.Info(
        title="MDD Backend API",
        default_version='v1',
        description="API documentation for the MDD project",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/monitoring/live/', LiveMonitorView.as_view(), name='live-monitor'),
    path('admin/', admin.site.urls),

    # Эндпоинт для метрик Prometheus (прямая передача функции)
    path('metrics/', ExportToDjangoView, name='prometheus-django-metrics'),  # <-- ИСПРАВЛЕНО ЗДЕСЬ

    # Все эндпоинты нашего API с префиксом /api/v1/
    path('api/v1/', include([
        path('auth/', include('apps.users.urls')),
        path('devices/', include('apps.devices.urls')),
        path('sos/', include('apps.sos.urls')),
        path('monitoring/', include('apps.monitoring.urls')),
    ])),

    # Документация API
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]