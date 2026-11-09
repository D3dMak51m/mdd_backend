from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class Role(models.Model):
    slug = models.SlugField(primary_key=True, help_text="Unique identifier (e.g. 'operator', 'supervisor')")
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    # Храним список прав как JSON: ["incidents.list", "incidents.resolve", "users.ban"]
    # Это быстрее, чем M2M таблица для проверки прав в high-load
    permissions = models.JSONField(default=list, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.slug})"


class UserRole(models.Model):
    """
    Связь пользователя с ролью.
    OneToOne, так как в операционной панели у сотрудника обычно одна четкая роль.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='rbac_role'
    )
    role = models.ForeignKey(Role, on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.user} -> {self.role}"