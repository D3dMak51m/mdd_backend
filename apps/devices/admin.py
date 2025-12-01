# apps/devices/admin.py

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse  # <-- ДОБАВЛЕН ЭТОТ ИМПОРТ
from unfold.admin import ModelAdmin
from unfold.decorators import display
from .models import Device, LocationTrack


@admin.register(Device)
class DeviceAdmin(ModelAdmin):
    # Добавили 'history_link' в list_display
    list_display = ('device_uid', 'model_badge', 'owner_link', 'battery_bar', 'status_badge', 'last_update',
                    'history_link')
    search_fields = ('device_uid', 'owner__phone_number', 'owner__full_name')
    list_filter = ('is_online', 'model', 'last_seen_via')

    @display(description="Model", label=True)
    def model_badge(self, obj):
        return obj.model

    @display(description="Owner")
    def owner_link(self, obj):
        return obj.owner.full_name or obj.owner.phone_number

    @display(
        description="Status",
        ordering="is_online",
        label={
            True: "success",  # Зеленый
            False: "default",  # Серый
        }
    )
    def status_badge(self, obj):
        return "ONLINE" if obj.is_online else "OFFLINE"

    # Прогресс-бар для батареи
    def battery_bar(self, obj):
        if obj.battery_level is None:
            return "-"

        # Логика цвета: <20% красный, <50% желтый, иначе зеленый
        color_class = "bg-green-500"
        if obj.battery_level < 20:
            color_class = "bg-red-500"
        elif obj.battery_level < 50:
            color_class = "bg-yellow-500"

        return format_html(
            f'<div class="w-24 bg-gray-200 rounded-full h-2.5 dark:bg-gray-700">'
            f'<div class="{color_class} h-2.5 rounded-full" style="width: {obj.battery_level}%"></div>'
            f'</div><div class="text-xs mt-1">{obj.battery_level}%</div>'
        )

    battery_bar.short_description = "Battery"

    # Ссылка на историю передвижений
    def history_link(self, obj):
        # Используем reverse для получения URL по имени
        url = reverse('device-history', args=[obj.device_uid])
        return format_html(
            '<a href="{}" class="text-blue-600 hover:text-blue-900 flex items-center gap-1">'
            '<span class="material-symbols-outlined text-sm">history</span> Трек'
            '</a>',
            url
        )

    history_link.short_description = "История"


@admin.register(LocationTrack)
class LocationTrackAdmin(ModelAdmin):
    list_display = ('device', 'created_at', 'speed', 'battery_level')