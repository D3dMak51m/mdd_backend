# apps/sos/views.py
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import SOSEvent
from .serializers import SOSEventTriggerSerializer, SOSEventSerializer


class SOSEventViewSet(viewsets.GenericViewSet):
    queryset = SOSEvent.objects.all()
    permission_classes = [IsAuthenticated]  # В будущем можно добавить кастомный пермишен для устройств

    @action(detail=False, methods=['post'], serializer_class=SOSEventTriggerSerializer)
    def trigger(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        event, created = serializer.save()  # .save() вызовет метод create() в сериализаторе

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

    @swagger_auto_schema(
        tags=['SOS'],
        operation_summary="Триггер SOS-события",
        operation_description="Принимает сигнал SOS от устройства или приложения, выполняет дедупликацию и запускает процесс оповещения."
    )
    @action(detail=False, methods=['post'], serializer_class=SOSEventTriggerSerializer)
    def trigger(self, request):
        return super().trigger(request)