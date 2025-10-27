# apps/monitoring/models.py
from django.db import models
from django.utils import timezone # Добавьте этот импорт

class SettingsConfig(models.Model):
    key = models.CharField(max_length=50, primary_key=True)
    value = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    updated_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.key