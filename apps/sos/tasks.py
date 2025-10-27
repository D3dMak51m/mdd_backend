# apps/sos/tasks.py
from celery import shared_task
from celery.utils.log import get_task_logger
from django.contrib.gis.measure import D
from django.contrib.gis.db.models.functions import Distance

from .models import SOSEvent
from apps.devices.models import Device
from apps.notifications.models import NotificationLog
from apps.notifications.tasks import send_push_notification
from apps.monitoring.models import SettingsConfig

logger = get_task_logger(__name__)


@shared_task
def notify_nearby_helpers(sos_id):
    """
    Находит ближайших помощников и отправляет им уведомления.
    """
    try:
        sos_event = SOSEvent.objects.get(id=sos_id)
    except SOSEvent.DoesNotExist:
        logger.error(f"SOSEvent с ID {sos_id} не найден.")
        return

    # Получаем радиус поиска из настроек, по умолчанию 5000 метров
    try:
        radius_setting = SettingsConfig.objects.get(key='SOS_RADIUS')
        radius_meters = int(radius_setting.value)
    except (SettingsConfig.DoesNotExist, ValueError):
        radius_meters = 5000  # Значение по умолчанию

    logger.info(f"Поиск помощников для SOS ID: {sos_id} в радиусе {radius_meters}м.")

    # Запрос PostGIS для поиска ближайших онлайн-устройств
    nearby_devices_owners = Device.objects.filter(
        is_online=True,
        owner__status='ACTIVE',
        last_latlon__isnull=False,
        last_latlon__dwithin=(sos_event.latlon, D(m=radius_meters))
    ).exclude(
        owner=sos_event.user  # Исключаем самого пользователя
    ).annotate(
        distance=Distance('last_latlon', sos_event.latlon)
    ).order_by('distance').values_list('owner_id', flat=True)[:50]

    if not nearby_devices_owners:
        logger.warning(f"Помощники для SOS ID {sos_id} не найдены.")
        # Здесь можно добавить логику эскалации, если никто не найден
        return "Помощники не найдены."

    message = f"Тревога! Рядом с вами нужна помощь. Событие: {sos_event.event_uid}"

    logs_created = []
    for owner_id in nearby_devices_owners:
        log = NotificationLog.objects.create(
            recipient_id=owner_id,
            sos_event=sos_event,
            notification_type=NotificationLog.NotificationType.PUSH,
            message=message,
        )
        logs_created.append(log.id)
        send_push_notification.delay(log.id)

    logger.info(f"Создано {len(logs_created)} уведомлений для SOS ID: {sos_id}.")
    return f"Создано {len(logs_created)} уведомлений."

@shared_task
def escalation_watch(sos_id):
    """
    Проверяет, было ли событие обработано, и эскалирует его при необходимости.
    """
    logger.info(f"Запущена задача escalation_watch для SOS ID: {sos_id}")
    # Логика будет добавлена позже
    return f"Проверка эскалации для SOS ID {sos_id} завершена."