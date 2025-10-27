# apps/notifications/admin.py

from django.contrib import admin
from .models import NotificationLog

@admin.register(NotificationLog)
class NotificationLogAdmin(admin.ModelAdmin):
    list_display = ('recipient', 'sos_event', 'notification_type', 'status', 'created_at')
    list_filter = ('notification_type', 'status')
    search_fields = ('recipient__phone_number', 'sos_event__event_uid')
    ordering = ('-created_at',)