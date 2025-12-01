# apps/devices/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DeviceViewSet, DeviceHistoryView

router = DefaultRouter()
router.register(r'', DeviceViewSet, basename='device')

urlpatterns = [
    path('history/<str:device_uid>/', DeviceHistoryView.as_view(), name='device-history'),
    path('', include(router.urls)),
]