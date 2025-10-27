# apps/sos/admin.py

from django.contrib.gis import admin
from .models import SOSEvent

@admin.register(SOSEvent)
class SOSEventAdmin(admin.GISModelAdmin):
    list_display = ('event_uid', 'user', 'device', 'detected_type', 'timestamp', 'resolved')
    list_filter = ('resolved', 'detected_type')
    search_fields = ('event_uid', 'user__phone_number', 'device__device_uid')
    ordering = ('-timestamp',)
    gis_field = 'latlon'