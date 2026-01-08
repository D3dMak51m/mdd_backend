# apps/audit/services.py

from .models import AuditLog
from .middleware import get_current_user, get_current_ip


class AuditService:
    @staticmethod
    def log(action, instance, changes=None, actor=None):
        """
        Создает запись в аудите.
        """
        # Если актор не передан явно, пытаемся достать из текущего контекста
        if not actor:
            actor = get_current_user()

        ip = get_current_ip()

        model_name = f"{instance._meta.app_label}.{instance._meta.model_name}"

        # Защита от слишком длинных строковых представлений
        target_str = str(instance)[:255]

        AuditLog.objects.create(
            actor=actor,
            ip_address=ip,
            action=action,
            target_model=model_name,
            target_id=str(instance.pk),
            target_str=target_str,
            changes=changes or {}
        )

    @staticmethod
    def get_diff(instance, old_instance):
        """
        Сравнивает старую и новую версию объекта.
        """
        changes = {}
        for field in instance._meta.fields:
            field_name = field.name

            # Пропускаем поля, которые не стоит логировать (например, пароли или updated_at)
            if field_name in ['password', 'updated_at', 'last_login']:
                continue

            try:
                old_val = getattr(old_instance, field_name)
                new_val = getattr(instance, field_name)

                # Для сравнения FK используем ID, чтобы не триггерить лишние запросы
                if field.is_relation and old_val != new_val:
                    old_val = getattr(old_instance, f"{field_name}_id", old_val)
                    new_val = getattr(instance, f"{field_name}_id", new_val)

                if old_val != new_val:
                    changes[field_name] = {
                        "old": str(old_val) if old_val is not None else None,
                        "new": str(new_val) if new_val is not None else None
                    }
            except Exception:
                continue
        return changes