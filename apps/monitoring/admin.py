# apps/monitoring/admin.py

from django.contrib import admin
from .models import SettingsConfig

@admin.register(SettingsConfig)
class SettingsConfigAdmin(admin.ModelAdmin):
    list_display = ('key', 'value', 'description', 'updated_at')
    search_fields = ('key', 'description')