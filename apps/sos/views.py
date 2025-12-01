# apps/sos/views.py

from datetime import timedelta
from django.utils import timezone
from django.db import transaction
from rest_framework import viewsets, status, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import SOSEvent
from .serializers import (
    SOSEventTriggerSerializer,
    SOSEventDetailSerializer,
    SOSRespondSerializer
)
from .tasks import notify_status_change


class SOSEventViewSet(mixins.RetrieveModelMixin,
                      mixins.ListModelMixin,
                      viewsets.GenericViewSet):
    queryset = SOSEvent.objects.all()
    permission_classes = [IsAuthenticated]
    lookup_field = 'event_uid'  # Используем UUID для поиска конкретного события

    def get_serializer_class(self):
        """
        Выбор сериализатора в зависимости от действия.
        """
        if self.action == 'trigger':
            return SOSEventTriggerSerializer
        if self.action == 'respond':
            return SOSRespondSerializer
        return SOSEventDetailSerializer

    def get_queryset(self):
        """
        Фильтрация событий.
        Если передан параметр ?active=true, возвращаем только актуальные и незавершенные события.
        """
        queryset = super().get_queryset()

        # Получаем параметр из URL
        active_only = self.request.query_params.get('active', None)

        if active_only == 'true':
            # 1. Отсекаем завершенные (по флагу и по статусу)
            queryset = queryset.filter(
                resolved=False
            ).exclude(
                status=SOSEvent.Status.RESOLVED
            )

            # 2. Отсекаем старые события (старше 24 часов),
            # чтобы карта не засорялась "зависшими" вызовами
            time_threshold = timezone.now() - timedelta(hours=24)
            queryset = queryset.filter(timestamp__gte=time_threshold)

        return queryset

    @swagger_auto_schema(
        tags=['SOS'],
        operation_summary="Список SOS-событий",
        operation_description="Возвращает список SOS-событий. Используйте ?active=true для получения только актуальных вызовов (для карты).",
        manual_parameters=[
            openapi.Parameter(
                'active',
                openapi.IN_QUERY,
                description="Если true, вернет только незавершенные события за последние 24 часа.",
                type=openapi.TYPE_BOOLEAN
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=['SOS'],
        operation_summary="Получить детали SOS-события",
        operation_description="Возвращает полную информацию о событии, включая данные пользователя и устройства."
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=['SOS'],
        operation_summary="Триггер SOS-события",
        operation_description="Принимает сигнал SOS от устройства или приложения, выполняет дедупликацию и запускает процесс оповещения.",
        request_body=SOSEventTriggerSerializer,
        responses={
            201: "Created (Событие создано)",
            200: "Duplicate (Событие проигнорировано как дубликат)"
        }
    )
    @action(detail=False, methods=['post'], serializer_class=SOSEventTriggerSerializer)
    def trigger(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Метод create сериализатора возвращает кортеж (instance, created)
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

    @swagger_auto_schema(
        tags=['SOS'],
        operation_summary="Принять вызов (Я еду)",
        operation_description="Позволяет помощнику принять вызов. Меняет статус события и уведомляет других.",
        request_body=SOSRespondSerializer,
        responses={
            200: "Вызов принят",
            409: "Вызов уже принят другим пользователем или завершен",
            404: "Событие не найдено"
        }
    )
    @action(detail=True, methods=['post'], serializer_class=SOSRespondSerializer)
    def respond(self, request, event_uid=None):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Используем транзакцию и select_for_update для блокировки строки,
        # чтобы избежать состояния гонки (Race Condition), если два человека нажмут одновременно.
        with transaction.atomic():
            try:
                # Блокируем строку базы данных до конца транзакции
                event = SOSEvent.objects.select_for_update().get(event_uid=event_uid)
            except SOSEvent.DoesNotExist:
                return Response({"detail": "Not found"}, status=status.HTTP_404_NOT_FOUND)

            # Проверка: не занят ли уже вызов
            if event.status != SOSEvent.Status.NEW:
                return Response(
                    {"detail": "Этот вызов уже принят другим пользователем или завершен."},
                    status=status.HTTP_409_CONFLICT
                )

            # Обновляем статус и назначаем исполнителя
            event.status = SOSEvent.Status.IN_PROGRESS
            event.accepted_by = request.user
            event.accepted_at = timezone.now()
            event.save()

        # Запускаем уведомления асинхронно (вне транзакции, чтобы не задерживать ответ)
        # notify_status_change уведомит пострадавшего и отменит вызов у других помощников
        notify_status_change.delay(event.id, request.user.id)

        return Response({"status": "accepted"}, status=status.HTTP_200_OK)