# apps/sos/tasks.py

from celery import shared_task
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)

@shared_task
def notify_nearby_helpers(sos_id):
    """
    Находит ближайших помощников и отправляет им уведомления.
    """
    logger.info(f"Запущена задача notify_nearby_helpers для SOS ID: {sos_id}")
    # Логика будет добавлена на Этапе 5
    return f"Уведомления для SOS ID {sos_id} поставлены в очередь."

@shared_task
def escalation_watch(sos_id):
    """
    Проверяет, было ли событие обработано, и эскалирует его при необходимости.
    """
    logger.info(f"Запущена задача escalation_watch для SOS ID: {sos_id}")
    # Логика будет добавлена позже
    return f"Проверка эскалации для SOS ID {sos_id} завершена."