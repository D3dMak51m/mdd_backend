# apps/notifications/models.py

from django.db import models
from django.conf import settings
from apps.sos.models import SOSEvent

class NotificationLog(models.Model):
    class NotificationType(models.TextChoices):
        PUSH = 'PUSH', 'Push Notification'
        WEBSOCKET = 'WEBSOCKET', 'WebSocket'
        SMS = 'SMS', 'SMS'

    class Status(models.TextChoices):
        QUEUED = 'QUEUED', 'Queued'
        SENT = 'SENT', 'Sent'
        FAILED = 'FAILED', 'Failed'
        READ = 'READ', 'Read'

    id = models.BigAutoField(primary_key=True)
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    sos_event = models.ForeignKey(SOSEvent, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=10, choices=NotificationType.choices)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.QUEUED)
    message = models.TextField()
    attempts = models.PositiveSmallIntegerField(default=0)
    last_attempt_at = models.DateTimeField(null=True, blank=True)
    response_payload = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Уведомление для {self.recipient.phone_number} о событии {self.sos_event.event_uid}"