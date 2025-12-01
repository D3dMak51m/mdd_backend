# apps/devices/views.py
import json
from django.contrib.auth.mixins import UserPassesTestMixin
from django.views.generic import DetailView
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Device, LocationTrack
from .serializers import DeviceSerializer, DeviceStatusUpdateSerializer, LocationTrackSerializer

class DeviceViewSet(viewsets.ModelViewSet):
    queryset = Device.objects.all()
    serializer_class = DeviceSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'device_uid'

    def get_queryset(self):
        # Пользователи могут видеть только свои устройства
        return self.queryset.filter(owner=self.request.user)

    def get_serializer_context(self):
        # Передаем request в контекст сериализатора
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context

    @action(detail=True, methods=['patch'], serializer_class=DeviceStatusUpdateSerializer)
    def status(self, request, device_uid=None):
        """
        Обновление статуса устройства (батарея, онлайн, местоположение).
        """
        device = self.get_object()
        serializer = self.get_serializer(instance=device, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        updated_device = serializer.save()

        response_serializer = DeviceSerializer(updated_device)
        return Response(response_serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], serializer_class=LocationTrackSerializer)
    def location(self, request, device_uid=None):
        """
        Запись нового местоположения для устройства.
        """
        device = self.get_object()
        serializer = self.get_serializer(data=request.data, context={'device': device})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'status': 'location recorded'}, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(tags=['Devices'], operation_summary="Регистрация нового устройства")
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(tags=['Devices'], operation_summary="Обновление статуса устройства")
    @action(detail=True, methods=['patch'], serializer_class=DeviceStatusUpdateSerializer)
    def status(self, request, device_uid=None):
        return super().status(request, device_uid)

    @swagger_auto_schema(tags=['Devices'], operation_summary="Запись местоположения устройства")
    @action(detail=True, methods=['post'], serializer_class=LocationTrackSerializer)
    def location(self, request, device_uid=None):
        return super().location(request, device_uid)


class DeviceHistoryView(UserPassesTestMixin, DetailView):
    model = Device
    template_name = 'admin/devices/history.html'
    context_object_name = 'device'
    slug_field = 'device_uid'
    slug_url_kwarg = 'device_uid'

    def test_func(self):
        return self.request.user.is_staff

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Получаем последние 100 точек трека
        tracks = LocationTrack.objects.filter(device=self.object).order_by('-created_at')[:100]

        # Формируем GeoJSON LineString
        coordinates = [[t.latlon.y, t.latlon.x] for t in tracks if t.latlon]

        context['track_json'] = json.dumps(coordinates)
        return context