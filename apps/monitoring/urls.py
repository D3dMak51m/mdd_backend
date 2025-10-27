# apps/monitoring/urls.py

from django.urls import path
from .views import SentryTestView

urlpatterns = [
    path('sentry-test/', SentryTestView.as_view(), name='sentry-test'),
]