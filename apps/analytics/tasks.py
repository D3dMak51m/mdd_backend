from celery import shared_task
from .services import AnalyticsService

@shared_task
def aggregate_daily_stats_task():
    """
    Фоновая задача для пересчета статистики.
    """
    # Пересчитываем за последнюю неделю, чтобы данные были актуальны
    AnalyticsService.recalculate_last_week()
    return "Daily stats aggregated successfully."