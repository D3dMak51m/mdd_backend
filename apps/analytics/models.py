from django.db import models


class DailyIncidentStats(models.Model):
    # Дата, за которую собрана статистика
    date = models.DateField(unique=True, db_index=True)

    # Основные метрики
    total_incidents = models.PositiveIntegerField(default=0)
    resolved_count = models.PositiveIntegerField(default=0)
    false_alarms = models.PositiveIntegerField(default=0)  # Например, отмененные пользователем

    # MTTR (Mean Time To Resolve) - среднее время реакции в секундах
    avg_response_time_seconds = models.FloatField(default=0.0)

    # JSON для гибкости (например, распределение по типам: {"FALL": 5, "MANUAL": 2})
    type_distribution = models.JSONField(default=dict, blank=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date']
        verbose_name = "Daily Statistic"
        verbose_name_plural = "Daily Statistics"

    def __str__(self):
        return f"Stats for {self.date}: {self.total_incidents} incidents"