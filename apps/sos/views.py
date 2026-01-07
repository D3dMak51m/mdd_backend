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
    SOSRespondSerializer,
    SOSResolveSerializer
)
from .tasks import notify_status_change


class SOSEventViewSet(mixins.RetrieveModelMixin,
                      mixins.ListModelMixin,
                      viewsets.GenericViewSet):
    queryset = SOSEvent.objects.all()
    permission_classes = [IsAuthenticated]
    lookup_field = 'event_uid'

    def get_serializer_class(self):
        if self.action == 'trigger':
            return SOSEventTriggerSerializer
        if self.action == 'respond':
            return SOSRespondSerializer
        if self.action == 'resolve':
            return SOSResolveSerializer
        return SOSEventDetailSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        active_only = self.request.query_params.get('active', None)

        if active_only == 'true':
            queryset = queryset.filter(resolved=False).exclude(status=SOSEvent.Status.RESOLVED)
            time_threshold = timezone.now() - timedelta(hours=24)
            queryset = queryset.filter(timestamp__gte=time_threshold)

        return queryset

    @swagger_auto_schema(
        tags=['SOS'],
        operation_summary="Список SOS-событий",
        manual_parameters=[
            openapi.Parameter('active', openapi.IN_QUERY, description="Только активные", type=openapi.TYPE_BOOLEAN)
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(tags=['SOS'], operation_summary="Детали SOS-события")
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=['SOS'],
        operation_summary="Триггер SOS",
        request_body=SOSEventTriggerSerializer,
        responses={201: "Created", 200: "Duplicate"}
    )
    @action(detail=False, methods=['post'], serializer_class=SOSEventTriggerSerializer)
    def trigger(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        event, created = serializer.save()
        if not created:
            return Response({"status": "duplicate", "event_uid": event.event_uid}, status=status.HTTP_200_OK)
        return Response({"status": "created", "event_uid": event.event_uid}, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        tags=['SOS'],
        operation_summary="Принять вызов",
        request_body=SOSRespondSerializer,
        responses={200: "Accepted", 409: "Conflict"}
    )
    @action(detail=True, methods=['post'], serializer_class=SOSRespondSerializer)
    def respond(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Получаем ID из URL (надежный способ для DRF actions)
        uid = self.kwargs.get(self.lookup_field)

        with transaction.atomic():
            try:
                event = SOSEvent.objects.select_for_update().get(event_uid=uid)
            except SOSEvent.DoesNotExist:
                return Response({"detail": "Not found"}, status=status.HTTP_404_NOT_FOUND)

            if event.status != SOSEvent.Status.NEW:
                return Response(
                    {"detail": "Этот вызов уже принят или завершен."},
                    status=status.HTTP_409_CONFLICT
                )

            event.status = SOSEvent.Status.IN_PROGRESS
            event.accepted_by = request.user
            event.accepted_at = timezone.now()
            event.save()

        notify_status_change.delay(event.id, request.user.id)
        return Response({"status": "accepted"}, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        tags=['SOS'],
        operation_summary="Завершить инцидент",
        request_body=SOSResolveSerializer,
        responses={200: "Resolved", 400: "Already resolved", 403: "Forbidden"}
    )
    @action(detail=True, methods=['post'], serializer_class=SOSResolveSerializer)
    def resolve(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        notes = serializer.validated_data.get('notes', '')

        # Получаем ID из URL
        uid = self.kwargs.get(self.lookup_field)

        with transaction.atomic():
            try:
                event = SOSEvent.objects.select_for_update().get(event_uid=uid)
            except SOSEvent.DoesNotExist:
                return Response({"detail": "Not found"}, status=status.HTTP_404_NOT_FOUND)

            if event.status == SOSEvent.Status.RESOLVED:
                return Response({"detail": "Уже завершен."}, status=status.HTTP_400_BAD_REQUEST)

            # Проверка прав
            is_responder = event.accepted_by == request.user
            is_owner = event.user == request.user
            is_admin = request.user.role == 'ADMIN' or request.user.is_staff

            if not (is_responder or is_owner or is_admin):
                return Response({"detail": "Нет прав."}, status=status.HTTP_403_FORBIDDEN)

            event.status = SOSEvent.Status.RESOLVED
            event.resolved = True
            event.resolved_by = request.user
            event.resolved_at = timezone.now()

            if notes:
                if not event.raw_payload: event.raw_payload = {}
                event.raw_payload['resolution_notes'] = notes

            event.save()

        return Response({"status": "resolved"}, status=status.HTTP_200_OK)