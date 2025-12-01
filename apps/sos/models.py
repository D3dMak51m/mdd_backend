# apps/sos/models.py

import uuid
from django.db import models
from django.conf import settings
from django.contrib.gis.db import models as gis_models
from apps.devices.models import Device


class SOSEvent(models.Model):
    class DetectedType(models.TextChoices):
        FALL = 'FALL_DETECTED', 'Fall Detected'
        MANUAL = 'MANUAL_TRIGGER', 'Manual Trigger'
        OTHER = 'OTHER', 'Other'

    class Status(models.TextChoices):
        NEW = 'NEW', 'New'
        IN_PROGRESS = 'IN_PROGRESS', 'In Progress'  # Кто-то выехал
        RESOLVED = 'RESOLVED', 'Resolved'  # Помощь оказана

    id = models.BigAutoField(primary_key=True)
    event_uid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    device = models.ForeignKey(Device, on_delete=models.SET_NULL, null=True, blank=True, related_name='sos_events')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
                             related_name='sos_events')

    latlon = gis_models.PointField(srid=4326, geography=True)
    altitude = models.FloatField(null=True, blank=True)
    detected_type = models.CharField(max_length=20, choices=DetectedType.choices, default=DetectedType.OTHER)
    severity = models.PositiveSmallIntegerField(default=1)
    timestamp = models.DateTimeField()

    resolved = models.BooleanField(default=False)
    resolved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name='resolved_sos')
    resolved_at = models.DateTimeField(null=True, blank=True)

    raw_payload = models.JSONField(null=True, blank=True)
    dedup_hash = models.CharField(max_length=64, db_index=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    status = models.CharField(max_length=20, choices=Status.choices, default=Status.NEW)

    # Кто принял вызов (едет на помощь)
    accepted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='accepted_sos'
    )
    accepted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['timestamp']),
        ]

    def __str__(self):
        return f"SOS Event {self.event_uid} at {self.timestamp}"