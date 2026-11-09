# apps/devices/tasks.py

from datetime import timedelta
from django.utils import timezone
from celery import shared_task
from celery.utils.log import get_task_logger
from .models import Device

logger = get_task_logger(__name__)


@shared_task
def check_device_heartbeats():
    """
    Проверяет устройства, которые давно не выходили на связь,
    и помечает их как OFFLINE.
    """
    # Порог времени: 10 минут
    threshold = timezone.now() - timedelta(minutes=10)

    # Находим устройства, которые онлайн, но молчат дольше порога
    stale_devices = Device.objects.filter(
        is_online=True,
        last_update__lt=threshold
    )

    count = stale_devices.count()

    if count > 0:
        # Массовое обновление (один SQL запрос)
        stale_devices.update(is_online=False)

        logger.info(f"Heartbeat Monitor: {count} устройств помечены как OFFLINE (нет связи > 10 мин).")

        # TODO: Здесь можно добавить отправку Push-уведомления владельцу:
        # "Связь с вашим устройством потеряна"
    else:
        logger.info("Heartbeat Monitor: Все онлайн-устройства на связи.")

    return f"Checked devices. {count} went offline."