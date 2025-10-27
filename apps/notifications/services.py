# apps/notifications/services.py

from firebase_admin import messaging
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)

def send_fcm_push(token: str, title: str, body: str, data: dict = None):
    """
    Отправляет одно push-уведомление на указанный токен.
    Возвращает ответ от FCM.
    """
    if not token:
        raise ValueError("FCM токен не предоставлен.")

    message = messaging.Message(
        notification=messaging.Notification(
            title=title,
            body=body,
        ),
        data=data or {},
        token=token,
    )

    try:
        response = messaging.send(message)
        logger.info(f"FCM-уведомление успешно отправлено: {response}")
        return response
    except Exception as e:
        logger.error(f"Ошибка при отправке FCM-уведомления на токен {token}: {e}")
        # Передаем исключение дальше, чтобы Celery мог его обработать
        raise