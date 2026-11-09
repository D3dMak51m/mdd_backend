# apps/sos/serializers.py

import hashlib
import math
from datetime import timedelta
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from rest_framework import serializers
from django.contrib.gis.geos import Point

from .models import SOSEvent
from apps.devices.models import Device
from apps.users.serializers import UserSerializer
from apps.devices.serializers import DeviceSerializer
from .tasks import notify_nearby_helpers, escalation_watch
from .consumers import DispatcherConsumer


class SOSEventTriggerSerializer(serializers.Serializer):
    device_uid = serializers.CharField(max_length=100)
    user_uuid = serializers.UUIDField(required=False)
    lat = serializers.FloatField(min_value=-90, max_value=90)
    lon = serializers.FloatField(min_value=-180, max_value=180)
    altitude = serializers.FloatField(required=False)
    detected_type = serializers.ChoiceField(choices=SOSEvent.DetectedType.choices)
    severity = serializers.IntegerField(min_value=1, max_value=5)
    timestamp = serializers.DateTimeField()
    raw_payload = serializers.JSONField()

    def create(self, validated_data):
        device_uid = validated_data['device_uid']
        timestamp = validated_data['timestamp']
        lat = validated_data['lat']
        lon = validated_data['lon']

        # 1. Вычисляем хэш для дедупликации
        ts_minute = math.floor(timestamp.timestamp() / 60)
        coords_str = f"{round(lat, 4)}{round(lon, 4)}"
        hash_string = f"{device_uid}{ts_minute}{coords_str}".encode('utf-8')
        dedup_hash = hashlib.sha256(hash_string).hexdigest()

        # 2. Проверяем наличие дубликата в пределах 5 минут
        time_threshold = timestamp - timedelta(minutes=5)
        existing_event = SOSEvent.objects.filter(
            dedup_hash=dedup_hash,
            timestamp__gte=time_threshold
        ).first()

        if existing_event:
            return existing_event, False

        # 3. Создаем событие
        try:
            device = Device.objects.get(device_uid=device_uid)
        except Device.DoesNotExist:
            raise serializers.ValidationError("Устройство с таким UID не найдено.")

        point = Point(lon, lat, srid=4326)

        event = SOSEvent.objects.create(
            device=device,
            user=device.owner,
            latlon=point,
            altitude=validated_data.get('altitude'),
            detected_type=validated_data['detected_type'],
            severity=validated_data['severity'],
            timestamp=timestamp,
            raw_payload=validated_data['raw_payload'],
            dedup_hash=dedup_hash,
            status=SOSEvent.Status.NEW
        )

        # 4. Запускаем фоновые задачи
        notify_nearby_helpers.delay(event.id)
        escalation_watch.apply_async(args=[event.id], countdown=300)

        # 5. Отправляем событие в WebSocket
        channel_layer = get_channel_layer()
        # Для вебсокета используем детальный сериализатор, чтобы фронт получил все данные сразу
        event_data = SOSEventDetailSerializer(event).data

        async_to_sync(channel_layer.group_send)(
            DispatcherConsumer.GROUP_NAME,
            {
                'type': 'sos.event.broadcast',
                'payload': event_data
            }
        )

        return event, True


class SOSRespondSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=['ACCEPTED'])


class SOSResolveSerializer(serializers.Serializer):
    notes = serializers.CharField(required=False, allow_blank=True, help_text="Комментарий к решению")


class SOSEventDetailSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    device = DeviceSerializer(read_only=True)
    accepted_by = UserSerializer(read_only=True)
    resolved_by = UserSerializer(read_only=True)

    lat = serializers.SerializerMethodField()
    lon = serializers.SerializerMethodField()

    class Meta:
        model = SOSEvent
        fields = (
            'id',
            'event_uid',
            'status',
            'timestamp',
            'resolved',
            'resolved_at',
            'resolved_by',
            'detected_type',
            'severity',
            'lat',
            'lon',
            'altitude',
            'user',
            'device',
            'accepted_by',
            'accepted_at',
            'created_at',
            'raw_payload'
        )

    def get_lat(self, obj):
        return obj.latlon.y if obj.latlon else None

    def get_lon(self, obj):
        return obj.latlon.x if obj.latlon else None