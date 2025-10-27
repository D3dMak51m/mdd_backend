# apps/devices/views.py

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Device
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