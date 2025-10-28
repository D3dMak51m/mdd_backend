# apps/sos/views.py (ИСПРАВЛЕННАЯ ВЕРСИЯ)

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from .models import SOSEvent
from .serializers import SOSEventTriggerSerializer


class SOSEventViewSet(viewsets.GenericViewSet):
    queryset = SOSEvent.objects.all()
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        tags=['SOS'],
        operation_summary="Триггер SOS-события",
        operation_description="Принимает сигнал SOS от устройства или приложения, выполняет дедупликацию и запускает процесс оповещения."
    )
    @action(detail=False, methods=['post'], serializer_class=SOSEventTriggerSerializer)
    def trigger(self, request):
        # Здесь должна быть реализация, а не вызов super()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        event, created = serializer.save()

        if not created:
            return Response({
                "status": "duplicate",
                "event_uid": event.event_uid
            }, status=status.HTTP_200_OK)

        response_data = {
            "status": "created",
            "event_uid": event.event_uid,
        }
        return Response(response_data, status=status.HTTP_201_CREATED)