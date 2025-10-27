# apps/sos/serializers.py

import hashlib
import math
from datetime import datetime, timedelta, timezone

from rest_framework import serializers
from django.contrib.gis.geos import Point

from .models import SOSEvent
from apps.devices.models import Device
from .tasks import notify_nearby_helpers, escalation_watch


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
        # SHA256(device_uid + floor(timestamp/60) + rounded_coords(4 dec))
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
            # Возвращаем существующее событие и флаг False (не создано)
            return existing_event, False

        # 3. Если дубликата нет, создаем новое событие
        try:
            device = Device.objects.get(device_uid=device_uid)
        except Device.DoesNotExist:
            raise serializers.ValidationError("Устройство с таким UID не найдено.")

        point = Point(lon, lat, srid=4326)

        event = SOSEvent.objects.create(
            device=device,
            user=device.owner,  # По умолчанию владелец устройства
            latlon=point,
            altitude=validated_data.get('altitude'),
            detected_type=validated_data['detected_type'],
            severity=validated_data['severity'],
            timestamp=timestamp,
            raw_payload=validated_data['raw_payload'],
            dedup_hash=dedup_hash
        )

        # 4. Запускаем фоновые задачи
        notify_nearby_helpers.delay(event.id)
        # Задача эскалации через 5 минут (300 секунд)
        escalation_watch.apply_async(args=[event.id], countdown=300)

        # Возвращаем новое событие и флаг True (создано)
        return event, True


class SOSEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = SOSEvent
        fields = ('event_uid', 'timestamp', 'resolved')