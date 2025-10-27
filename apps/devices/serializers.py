# apps/devices/serializers.py

from rest_framework import serializers
from django.contrib.gis.geos import Point
from django.utils import timezone
from .models import Device, LocationTrack
from apps.users.models import User


class DeviceSerializer(serializers.ModelSerializer):
    owner_uuid = serializers.UUIDField(write_only=True, source='owner.uuid', required=False)

    class Meta:
        model = Device
        fields = (
            'uuid', 'device_uid', 'owner_uuid', 'model', 'battery_level',
            'is_online', 'last_update', 'sim_number', 'last_seen_via'
        )
        read_only_fields = ('uuid', 'battery_level', 'is_online', 'last_update', 'last_seen_via')

    def create(self, validated_data):
        # Владельцем устройства становится пользователь, отправивший запрос
        owner = self.context['request'].user
        device = Device.objects.create(owner=owner, **validated_data)
        return device


class DeviceStatusUpdateSerializer(serializers.Serializer):
    battery_level = serializers.IntegerField(required=False, min_value=0, max_value=100)
    is_online = serializers.BooleanField(required=False)
    lat = serializers.FloatField(required=False, min_value=-90, max_value=90)
    lon = serializers.FloatField(required=False, min_value=-180, max_value=180)
    last_seen_via = serializers.ChoiceField(choices=Device.LastSeenVia.choices, required=False)

    def update(self, instance, validated_data):
        instance.battery_level = validated_data.get('battery_level', instance.battery_level)
        instance.is_online = validated_data.get('is_online', instance.is_online)
        instance.last_seen_via = validated_data.get('last_seen_via', instance.last_seen_via)
        instance.last_update = timezone.now()

        lat = validated_data.get('lat')
        lon = validated_data.get('lon')

        if lat is not None and lon is not None:
            point = Point(lon, lat, srid=4326)
            instance.last_latlon = point
            LocationTrack.objects.create(
                device=instance,
                latlon=point,
                battery_level=instance.battery_level
            )

        instance.save()
        return instance


class LocationTrackSerializer(serializers.ModelSerializer):
    lat = serializers.FloatField(write_only=True, min_value=-90, max_value=90)
    lon = serializers.FloatField(write_only=True, min_value=-180, max_value=180)

    class Meta:
        model = LocationTrack
        fields = ('lat', 'lon', 'speed', 'direction', 'battery_level', 'created_at')
        read_only_fields = ('created_at',)

    def create(self, validated_data):
        device = self.context['device']
        lat = validated_data.pop('lat')
        lon = validated_data.pop('lon')
        point = Point(lon, lat, srid=4326)

        track = LocationTrack.objects.create(device=device, latlon=point, **validated_data)

        device.last_latlon = point
        device.last_update = track.created_at
        device.battery_level = track.battery_level
        device.is_online = True
        device.save()

        return track