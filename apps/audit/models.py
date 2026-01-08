from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class AuditLog(models.Model):
    ACTION_LOGIN = 'LOGIN'
    ACTION_LOGOUT = 'LOGOUT'
    ACTION_CREATE = 'CREATE'
    ACTION_UPDATE = 'UPDATE'
    ACTION_DELETE = 'DELETE'
    ACTION_RESOLVE = 'RESOLVE'

    ACTION_CHOICES = [
        (ACTION_LOGIN, 'Login'),
        (ACTION_LOGOUT, 'Logout'),
        (ACTION_CREATE, 'Create'),
        (ACTION_UPDATE, 'Update'),
        (ACTION_DELETE, 'Delete'),
        (ACTION_RESOLVE, 'Resolve Incident'),
    ]

    id = models.BigAutoField(primary_key=True)

    # Кто совершил действие (может быть NULL, если это системная задача)
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='audit_logs'
    )

    # IP адрес (важно для безопасности)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    # Тип действия
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)

    # Над чем совершено действие (Generic Relations не используем для скорости, храним строками)
    target_model = models.CharField(max_length=100, help_text="e.g. 'sos.SOSEvent'")
    target_id = models.CharField(max_length=100)
    target_str = models.CharField(max_length=255, blank=True, help_text="String representation of the object")

    # Детали изменений: { "field": {"old": "val1", "new": "val2"} }
    changes = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['created_at']),
            models.Index(fields=['action']),
            models.Index(fields=['actor']),
            models.Index(fields=['target_model', 'target_id']),
        ]

    def __str__(self):
        return f"[{self.created_at}] {self.actor}: {self.action} -> {self.target_model}"