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
    Основная функция для генерации данных Дашборда с улучшенным дизайном.
    """

    # --- 1. Сбор метрик (KPI) с градиентами ---
    active_sos_count = SOSEvent.objects.filter(resolved=False).count()
    online_devices_count = Device.objects.filter(is_online=True).count()
    total_devices = Device.objects.count()
    sos_today = SOSEvent.objects.filter(timestamp__date=timezone.now().date()).count()
    total_users = User.objects.count()

    # Расчет трендов (пример)
    yesterday = timezone.now().date() - timedelta(days=1)
    sos_yesterday = SOSEvent.objects.filter(timestamp__date=yesterday).count()
    sos_trend = round(((sos_today - sos_yesterday) / max(sos_yesterday, 1)) * 100, 1) if sos_yesterday else 0

    # Формируем карточки KPI с градиентами
    kpi = [
        {
            "title": "АКТИВНЫЕ ТРЕВОГИ",
            "metric": active_sos_count,
            "footer": "Требуют реакции",
            "footer_icon": "warning",
            "icon": "emergency",
            "gradient_from": "red",
            "gradient_to": "orange",
            "trend": None,
        },
        {
            "title": "Устройств Онлайн",
            "metric": f"{online_devices_count} / {total_devices}",
            "footer": "Мониторинг сети",
            "footer_icon": "wifi",
            "icon": "router",
            "gradient_from": "emerald",
            "gradient_to": "teal",
            "trend": None,
        },
        {
            "title": "Инцидентов сегодня",
            "metric": sos_today,
            "footer": timezone.now().strftime("%d.%m.%Y"),
            "footer_icon": "calendar_today",
            "icon": "timeline",
            "gradient_from": "amber",
            "gradient_to": "orange",
            "trend": sos_trend,
        },
        {
            "title": "Всего пользователей",
            "metric": total_users,
            "footer": "База данных",
            "footer_icon": "database",
            "icon": "group",
            "gradient_from": "blue",
            "gradient_to": "indigo",
            "trend": None,
        },
    ]

    # --- 2. Подготовка данных для Графика (Линейный - SOS за 7 дней) ---
    last_7_days = timezone.now() - timedelta(days=7)

    sos_by_day = (
        SOSEvent.objects.filter(timestamp__gte=last_7_days)
        .annotate(day=TruncDay('timestamp'))
        .values('day')
        .annotate(count=Count('id'))
        .order_by('day')
    )

    days_labels = []
    days_data = []

    for i in range(7):
        date_cursor = (timezone.now() - timedelta(days=6 - i)).date()
        days_labels.append(date_cursor.strftime("%d.%m"))
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

    # --- 4. Подготовка данных для Карты Флота ---
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
            "icon": "timeline",
            "labels": days_labels,
            "datasets": [
                {
                    "label": "Количество SOS",
                    "data": days_data,
                }
            ],
            "stats": [
                {"label": "Сегодня", "value": sos_today},
                {"label": "Всего за неделю", "value": sum(days_data)},
                {"label": "Среднее/день", "value": round(sum(days_data) / 7, 1)},
            ]
        },
        {
            "title": "Типы угроз",
            "type": "doughnut",
            "icon": "pie_chart",
            "labels": type_labels,
            "datasets": [
                {
                    "data": type_data,
                }
            ],
        },
    ]

    # --- 6. Обновление контекста ---
    context.update({
        "kpi": kpi,
        "devices_json": json.dumps(devices_map_data, cls=DjangoJSONEncoder),
        "charts_json": json.dumps(charts_config, cls=DjangoJSONEncoder),
        "charts": charts_config,
        "navigation": [
            {
                "title": "Открыть Live Monitor",
                "link": "/admin/monitoring/live/",
                "icon": "emergency",
                "description": "Мониторинг в реальном времени"
            },
            {
                "title": "Список устройств",
                "link": "/admin/devices/device/",
                "icon": "watch",
                "description": "Управление устройствами"
            },
            {
                "title": "SOS События",
                "link": "/admin/sos/sosevent/",
                "icon": "notifications_active",
                "description": "История инцидентов"
            },
        ]
    })

    return context