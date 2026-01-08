from django.core.cache import cache
from django.conf import settings
from .models import UserRole

class RBACService:
    CACHE_TIMEOUT = 3600  # 1 час
    CACHE_KEY_PREFIX = "rbac:perms:"

    @classmethod
    def get_user_permissions(cls, user) -> set:
        """
        Возвращает сет пермишенов пользователя.
        Сначала ищет в Redis, потом в БД.
        """
        if not user.is_authenticated:
            return set()

        # Superuser имеет все права (god mode)
        if user.is_superuser:
            return {"*"}

        cache_key = f"{cls.CACHE_KEY_PREFIX}{user.id}"
        cached_perms = cache.get(cache_key)

        if cached_perms is not None:
            return set(cached_perms)

        # Fallback to DB
        try:
            user_role = UserRole.objects.select_related('role').get(user=user)
            perms = set(user_role.role.permissions)
        except UserRole.DoesNotExist:
            perms = set()

        # Cache it
        cache.set(cache_key, list(perms), timeout=cls.CACHE_TIMEOUT)
        return perms

    @classmethod
    def has_permission(cls, user, permission: str) -> bool:
        """
        Проверка конкретного права.
        """
        perms = cls.get_user_permissions(user)
        if "*" in perms:
            return True
        return permission in perms

    @classmethod
    def clear_cache(cls, user_id):
        """
        Сброс кэша при изменении роли (вызывать в сигналах)
        """
        cache.delete(f"{cls.CACHE_KEY_PREFIX}{user_id}")