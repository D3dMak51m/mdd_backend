from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import UserRole, Role
from .services import RBACService

@receiver([post_save, post_delete], sender=UserRole)
def invalidate_user_cache(sender, instance, **kwargs):
    RBACService.clear_cache(instance.user.id)

@receiver([post_save], sender=Role)
def invalidate_role_cache(sender, instance, **kwargs):
    # Если изменилась сама роль, нужно сбросить кэш всех пользователей с этой ролью.
    # Это тяжелая операция, но роли меняются редко.
    # Для MVP можно просто сбрасывать ключи по паттерну или ждать TTL.
    # В production лучше использовать версионирование ключей, но пока оставим TTL.
    pass