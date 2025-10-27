# apps/devices/models.py

import uuid
from django.db import models
from django.conf import settings
from django.contrib.gis.db import models as gis_models


class Device(models.Model):
    class LastSeenVia(models.TextChoices):
        BLE = 'BLE', 'Bluetooth Low Energy'
        HTTP = 'HTTP', 'HTTP'
        LTE = 'LTE', 'LTE'

    id = models.BigAutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    device_uid = models.CharField(max_length=100, unique=True, help_text="Уникальный идентификатор устройства")
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='devices')
    model = models.CharField(max_length=50)
    battery_level = models.PositiveSmallIntegerField(null=True, blank=True)
    is_online = models.BooleanField(default=False)
    last_latlon = gis_models.PointField(srid=4326, null=True, blank=True, geography=True)
    last_update = models.DateTimeField(null=True, blank=True)
    sim_number = models.CharField(max_length=20, blank=True, null=True)
    last_seen_via = models.CharField(max_length=4, choices=LastSeenVia.choices, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.model} ({self.device_uid})"


class LocationTrack(models.Model):
    id = models.BigAutoField(primary_key=True)
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='tracks')
    latlon = gis_models.PointField(srid=4326, geography=True)
    speed = models.FloatField(null=True, blank=True)
    direction = models.FloatField(null=True, blank=True, help_text="Направление в градусах")
    battery_level = models.PositiveSmallIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['device', '-created_at']),
        ]

    def __str__(self):
        return f"Трек для {self.device.device_uid} в {self.created_at}"