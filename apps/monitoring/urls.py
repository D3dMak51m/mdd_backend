# apps/monitoring/urls.py

from django.urls import path
from .views import SentryTestView, LiveMonitorView

urlpatterns = [
    path('sentry-test/', SentryTestView.as_view(), name='sentry-test'),
    path('live/', LiveMonitorView.as_view(), name='live-monitor'),
]