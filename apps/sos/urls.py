# apps/sos/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SOSEventViewSet

router = DefaultRouter()
router.register(r'', SOSEventViewSet, basename='sos')

urlpatterns = [
    path('', include(router.urls)),
]