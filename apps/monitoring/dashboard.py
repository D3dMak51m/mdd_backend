# apps/monitoring/dashboard.py

import json
from datetime import timedelta
from django.utils import timezone
from django.db.models import Count
from django.db.models.functions import TruncDay
from django.core.serializers.json import DjangoJSONEncoder
from django.utils.translation import gettext_lazy as _

from apps.sos.models import SOSEvent
from apps.devices.models import Device
from apps.users.models import User


def badge_active_sos(request):
    """
    Возвращает количество активных (нерешенных) SOS-сигналов
    для отображения в красном бейдже в боковом меню.
    """
    return SOSEvent.objects.filter(resolved=False).count()


def dashboard_callback(request, context):
    """
    Основная функция для генерации данных Дашборда (Главная страница админки).
    """

    # --- 1. Сбор метрик (KPI) ---
    active_sos_count = SOSEvent.objects.filter(resolved=False).count()
    online_devices_count = Device.objects.filter(is_online=True).count()
    total_devices = Device.objects.count()
    sos_today = SOSEvent.objects.filter(timestamp__date=timezone.now().date()).count()
    total_users = User.objects.count()

    # Формируем карточки KPI
    kpi = [
        {
            "title": "АКТИВНЫЕ ТРЕВОГИ",
            "metric": active_sos_count,
            "footer": "Требуют реакции",
            "color": "text-red-600",  # Ярко-красный текст
            "icon": "warning",
        },
        {
            "title": "Устройств Онлайн",
            "metric": f"{online_devices_count} / {total_devices}",
            "footer": "Мониторинг сети",
            "color": "text-emerald-600",  # Ярко-зеленый текст
            "icon": "router",
        },
        {
            "title": "Инцидентов за сегодня",
            "metric": sos_today,
            "footer": timezone.now().strftime("%d.%m.%Y"),
            "color": "text-amber-600",  # Янтарный текст
            "icon": "history",
        },
        {
            "title": "Всего пользователей",
            "metric": total_users,
            "footer": "База данных",
            "color": "text-blue-600",  # Синий текст
            "icon": "group",
        },
    ]    # --- 2. Подготовка данных для Графика (Линейный - SOS за 7 дней) ---
    last_7_days = timezone.now() - timedelta(days=7)

    # Агрегация по дням
    sos_by_day = (
        SOSEvent.objects.filter(timestamp__gte=last_7_days)
        .annotate(day=TruncDay('timestamp'))
        .values('day')
        .annotate(count=Count('id'))
        .order_by('day')
    )

    # Заполнение пропущенных дней нулями
    days_labels = []
    days_data = []

    for i in range(7):
        # Идем от 6 дней назад до сегодня
        date_cursor = (timezone.now() - timedelta(days=6 - i)).date()
        days_labels.append(date_cursor.strftime("%d.%m"))

        # Ищем, есть ли данные за этот день
        val = next((item['count'] for item in sos_by_day if item['day'].date() == date_cursor), 0)
        days_data.append(val)

    # --- 3. Подготовка данных для Графика (Круговой - Типы угроз) ---
    sos_types = (
        SOSEvent.objects.values('detected_type')
        .annotate(count=Count('id'))
        .order_by('-count')
    )

    type_labels = [item['detected_type'] for item in sos_types]
    type_data = [item['count'] for item in sos_types]

    # --- 4. Подготовка данных для Карты Флота (Все устройства) ---
    # Берем только устройства, у которых есть координаты
    devices_qs = Device.objects.filter(last_latlon__isnull=False).select_related('owner')

    devices_map_data = []
    for d in devices_qs:
        devices_map_data.append({
            "uid": d.device_uid,
            "model": d.model,
            "owner": d.owner.full_name or d.owner.phone_number,
            "lat": d.last_latlon.y,
            "lon": d.last_latlon.x,
            "is_online": d.is_online,
            "battery": d.battery_level
        })

    # --- 5. Формирование конфигурации графиков ---
    charts_config = [
        {
            "title": "Динамика инцидентов (7 дней)",
            "type": "line",
            "labels": days_labels,
            "datasets": [
                {
                    "label": "Количество SOS",
                    "data": days_data,
                    "borderColor": "#dc2626",  # red-600
                    "backgroundColor": "rgba(220, 38, 38, 0.1)",
                    "fill": True,
                    "tension": 0.4,  # Сглаживание линий
                }
            ],
        },
        {
            "title": "Типы угроз",
            "type": "doughnut",
            "labels": type_labels,
            "datasets": [
                {
                    "data": type_data,
                    "backgroundColor": [
                        "#ef4444",  # red
                        "#f97316",  # orange
                        "#3b82f6",  # blue
                        "#a855f7",  # purple
                        "#10b981",  # emerald
                    ],
                }
            ],
        },
    ]

    # --- 6. Обновление контекста ---
    context.update({
        "kpi": kpi,
        # JSON строки для использования в JavaScript
        "devices_json": json.dumps(devices_map_data, cls=DjangoJSONEncoder),
        "charts_json": json.dumps(charts_config, cls=DjangoJSONEncoder),

        # Объект charts нужен для цикла в шаблоне (чтобы создать canvas элементы)
        "charts": charts_config,

        # Дополнительная навигация на дашборде (опционально)
        "navigation": [
            {"title": "Открыть Live Monitor", "link": "/admin/monitoring/live/", "icon": "public"},
            {"title": "Список устройств", "link": "/admin/devices/device/", "icon": "watch"},
        ]
    })

    return context