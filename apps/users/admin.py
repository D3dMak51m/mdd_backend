# apps/users/admin.py

from django.contrib import admin
from .models import User

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('phone_number', 'full_name', 'role', 'status', 'is_staff', 'date_joined')
    list_filter = ('role', 'status', 'is_staff')
    search_fields = ('phone_number', 'full_name', 'email')
    ordering = ('-date_joined',)