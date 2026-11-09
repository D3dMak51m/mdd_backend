from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from apps.sos.models import SOSEvent
from apps.users.models import User
from apps.rbac.models import Role
from .services import AuditService
from .models import AuditLog

# Список моделей для аудита
AUDITED_MODELS = [SOSEvent, User, Role]

@receiver(pre_save)
def audit_pre_save(sender, instance, **kwargs):
    if sender in AUDITED_MODELS and instance.pk:
        # Пытаемся получить старую версию из БД для сравнения
        try:
            old_instance = sender.objects.get(pk=instance.pk)
            instance._old_instance = old_instance
        except sender.DoesNotExist:
            instance._old_instance = None

@receiver(post_save)
def audit_post_save(sender, instance, created, **kwargs):
    if sender not in AUDITED_MODELS:
        return

    if created:
        AuditService.log(AuditLog.ACTION_CREATE, instance)
    else:
        # Вычисляем разницу
        old_instance = getattr(instance, '_old_instance', None)
        if old_instance:
            changes = AuditService.get_diff(instance, old_instance)
            if changes: # Логируем только если были реальные изменения
                AuditService.log(AuditLog.ACTION_UPDATE, instance, changes=changes)

@receiver(post_delete)
def audit_post_delete(sender, instance, **kwargs):
    if sender in AUDITED_MODELS:
        AuditService.log(AuditLog.ACTION_DELETE, instance)