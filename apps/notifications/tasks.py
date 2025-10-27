# apps/notifications/tasks.py (обновленный)

from celery import shared_task
from celery.utils.log import get_task_logger
from django.utils import timezone

from .models import NotificationLog
from .services import send_fcm_push

logger = get_task_logger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_push_notification(self, log_id):
    """
    Отправляет push-уведомление через FCM с логикой повторов.
    """
    try:
        log = NotificationLog.objects.select_related('recipient').get(id=log_id)
    except NotificationLog.DoesNotExist:
        logger.error(f"NotificationLog с ID {log_id} не найден.")
        return

    log.attempts += 1
    log.last_attempt_at = timezone.now()

    recipient = log.recipient
    if not recipient.fcm_token:
        log.status = NotificationLog.Status.FAILED
        log.response_payload = {'error': 'FCM токен отсутствует у получателя.'}
        log.save()
        logger.warning(
            f"У получателя {recipient.phone_number} отсутствует FCM токен. Уведомление {log_id} не отправлено.")
        return

    try:
        title = "Тревога!"
        body = log.message
        data = {
            'sos_event_uid': str(log.sos_event.event_uid),
            'notification_id': str(log.id)
        }

        response = send_fcm_push(
            token=recipient.fcm_token,
            title=title,
            body=body,
            data=data
        )

        log.status = NotificationLog.Status.SENT
        log.response_payload = {'response': response}
        log.save()

        logger.info(f"Уведомление {log_id} успешно отправлено.")
        return f"Уведомление {log_id} успешно отправлено."

    except Exception as exc:
        logger.error(f"Ошибка при отправке уведомления {log_id}: {exc}")
        log.status = NotificationLog.Status.FAILED
        log.response_payload = {'error': str(exc)}
        log.save()
        # Celery автоматически повторит задачу из-за raise
        raise self.retry(exc=exc)