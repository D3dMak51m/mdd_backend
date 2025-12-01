# apps/sos/admin.py

from django.contrib import admin
from django.utils.html import format_html
from unfold.admin import ModelAdmin
from unfold.decorators import display
from .models import SOSEvent

@admin.register(SOSEvent)
class SOSEventAdmin(ModelAdmin):
    list_display = ('event_uid_short', 'user_info', 'type_badge', 'severity_badge', 'status_badge', 'timestamp')
    list_filter = ('status', 'detected_type', 'severity')
    search_fields = ('event_uid', 'user__phone_number')
    ordering = ('-timestamp',)

    def event_uid_short(self, obj):
        return str(obj.event_uid)[:8]
    event_uid_short.short_description = "ID"

    @display(description="User")
    def user_info(self, obj):
        if not obj.user: return "Unknown"
        return f"{obj.user.full_name} ({obj.user.phone_number})"

    @display(description="Type", label=True)
    def type_badge(self, obj):
        return obj.detected_type

    @display(
        description="Status",
        label={
            SOSEvent.Status.NEW: "danger",       # Красный
            SOSEvent.Status.IN_PROGRESS: "warning", # Желтый
            SOSEvent.Status.RESOLVED: "success",    # Зеленый
        }
    )
    def status_badge(self, obj):
        return obj.get_status_display()

    @display(description="Severity")
    def severity_badge(self, obj):
        # Визуализация серьезности (1-5) точками
        color = "text-red-500" if obj.severity >= 4 else "text-yellow-500"
        dots = "●" * obj.severity
        empty = "○" * (5 - obj.severity)
        return format_html(f'<span class="{color} text-lg">{dots}</span><span class="text-gray-300">{empty}</span>')