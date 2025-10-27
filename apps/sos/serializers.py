# apps/sos/serializers.py
import hashlib
import math
from datetime import timedelta
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from rest_framework import serializers
from django.contrib.gis.geos import Point

from .consumers import DispatcherConsumer
from .models import SOSEvent
from apps.devices.models import Device
from .tasks import notify_nearby_helpers, escalation_watch
from django_prometheus.models import model_deletes, model_inserts, model_updates

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

        model_inserts.labels(model=SOSEvent._meta.model_name).inc()

        # 4. Запускаем фоновые задачи
        notify_nearby_helpers.delay(event.id)
        escalation_watch.apply_async(args=[event.id], countdown=300)

        # 5. Отправляем событие в WebSocket-группу (НОВОЕ)
        channel_layer = get_channel_layer()
        event_data = SOSEventSerializer(event).data

        async_to_sync(channel_layer.group_send)(
            DispatcherConsumer.GROUP_NAME,
            {
                'type': 'sos.event.broadcast',  # Это имя вызовет метод sos_event_broadcast в consumer
                'payload': event_data
            }
        )

        return event, True


class SOSEventSerializer(serializers.ModelSerializer):
    device_uid = serializers.CharField(source='device.device_uid', read_only=True)
    user_phone = serializers.CharField(source='user.phone_number', read_only=True)
    lat = serializers.SerializerMethodField()
    lon = serializers.SerializerMethodField()

    class Meta:
        model = SOSEvent
        fields = (
            'event_uid', 'timestamp', 'resolved', 'detected_type', 'severity',
            'device_uid', 'user_phone', 'lat', 'lon'
        )

    def get_lat(self, obj):
        return obj.latlon.y

    def get_lon(self, obj):
        return obj.latlon.x

