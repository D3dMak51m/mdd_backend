# apps/devices/admin.py

from django.contrib.gis import admin
from .models import Device, LocationTrack

@admin.register(Device)
class DeviceAdmin(admin.GISModelAdmin):
    list_display = ('device_uid', 'owner', 'model', 'is_online', 'battery_level', 'last_update')
    list_filter = ('is_online', 'model')
    search_fields = ('device_uid', 'owner__phone_number')
    ordering = ('-last_update',)
    gis_field = 'last_latlon' # Указываем поле для отображения на карте

@admin.register(LocationTrack)
class LocationTrackAdmin(admin.GISModelAdmin):
    list_display = ('device', 'created_at', 'speed', 'battery_level')
    list_filter = ('device',)
    search_fields = ('device__device_uid',)
    ordering = ('-created_at',)
    gis_field = 'latlon'