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
from django.utils import timezone
from apps.notifications.services import send_fcm_push
from ..users.models import User

logger = get_task_logger(__name__)


@shared_task
def notify_status_change(sos_id, responder_id):
    """
    1. Уведомляет пострадавшего, что помощь едет.
    2. Уведомляет остальных помощников, что вызов принят другим.
    """
    try:
        sos_event = SOSEvent.objects.select_related('user', 'device').get(id=sos_id)
        responder = User.objects.get(id=responder_id)
    except (SOSEvent.DoesNotExist, User.DoesNotExist):
        return

    # 1. Уведомление ПОСТРАДАВШЕМУ
    if sos_event.user and sos_event.user.fcm_token:
        try:
            send_fcm_push(
                token=sos_event.user.fcm_token,
                title="Помощь в пути!",
                body=f"{responder.full_name} принял ваш вызов и направляется к вам.",
                data={
                    "type": "SOS_ACCEPTED",
                    "sos_id": str(sos_event.event_uid),
                    "responder_phone": responder.phone_number
                }
            )
        except Exception as e:
            logger.error(f"Не удалось уведомить пострадавшего: {e}")

    # 2. Уведомление ОСТАЛЬНЫМ ПОМОЩНИКАМ (Отмена)
    # Находим всех, кому мы отправляли пуш об этом событии, КРОМЕ того, кто принял
    other_notifications = NotificationLog.objects.filter(
        sos_event=sos_event,
        notification_type=NotificationLog.NotificationType.PUSH
    ).exclude(recipient_id=responder_id)

    for log in other_notifications:
        if log.recipient.fcm_token:
            try:
                send_fcm_push(
                    token=log.recipient.fcm_token,
                    title="Вызов принят",
                    body="Другой пользователь уже выехал на помощь. Спасибо за готовность!",
                    data={
                        "type": "SOS_CANCELLED_FOR_OTHERS",
                        "sos_id": str(sos_event.event_uid)
                    }
                )
            except Exception:
                continue


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
    Проверяет, был ли принят вызов. Если нет — эскалирует (уведомляет админов).
    """
    try:
        event = SOSEvent.objects.get(id=sos_id)
    except SOSEvent.DoesNotExist:
        return

    # Если событие уже принято или решено — ничего не делаем
    if event.status != SOSEvent.Status.NEW:
        logger.info(f"SOS {sos_id} уже обработан (Статус: {event.status}). Эскалация не требуется.")
        return

    logger.warning(f"SOS {sos_id} не принят в течение тайм-аута! Эскалация.")

    # 1. Находим всех админов/диспетчеров
    admins = User.objects.filter(role=User.Role.ADMIN, fcm_token__isnull=False)

    # 2. Отправляем им критическое уведомление
    count = 0
    for admin in admins:
        try:
            send_fcm_push(
                token=admin.fcm_token,
                title="⚠️ ЭСКАЛАЦИЯ SOS!",
                body=f"Инцидент {event.event_uid} не принят уже 5 минут! Требуется вмешательство.",
                data={
                    "type": "SOS_ESCALATION",
                    "sos_id": str(event.event_uid)
                }
            )
            count += 1
        except Exception:
            pass

    # 3. Можно также повысить severity в базе
    if event.severity < 5:
        event.severity = 5
        event.save(update_fields=['severity'])

    return f"Эскалация выполнена. Уведомлено {count} админов."
