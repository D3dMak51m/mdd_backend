# apps/notifications/tasks.py

from celery import shared_task
from celery.utils.log import get_task_logger
from .models import NotificationLog

logger = get_task_logger(__name__)

@shared_task(bind=True, max_retries=3)
def send_push_notification(self, log_id):
    """
    Отправляет push-уведомление через FCM.
    """
    try:
        log = NotificationLog.objects.get(id=log_id)
        logger.info(
            f"Отправка push-уведомления получателю {log.recipient.phone_number} "
            f"с токеном {log.recipient.fcm_token}"
        )
        # Здесь будет логика интеграции с FCM (Этап 6)
        # Имитируем успешную отправку
        log.status = NotificationLog.Status.SENT
        log.save()
        return f"Уведомление {log_id} успешно отправлено."
    except NotificationLog.DoesNotExist:
        logger.error(f"NotificationLog с ID {log_id} не найден.")
    except Exception as exc:
        logger.error(f"Ошибка при отправке уведомления {log_id}: {exc}")
        self.retry(exc=exc, countdown=60) # Повторить через 60 секунд