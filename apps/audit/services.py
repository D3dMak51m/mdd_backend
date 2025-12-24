from django.forms.models import model_to_dict
from .models import AuditLog
from .middleware import get_current_user, get_current_ip


class AuditService:
    @staticmethod
    def log(action, instance, changes=None, actor=None):
        """
        Создает запись в аудите.
        """
        if not actor:
            actor = get_current_user()
            # Если пользователя нет (например, Celery), actor останется None
            if actor and not actor.is_authenticated:
                actor = None

        ip = get_current_ip()

        model_name = f"{instance._meta.app_label}.{instance._meta.model_name}"

        AuditLog.objects.create(
            actor=actor,
            ip_address=ip,
            action=action,
            target_model=model_name,
            target_id=str(instance.pk),
            target_str=str(instance)[:255],
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
            try:
                old_val = getattr(old_instance, field_name)
                new_val = getattr(instance, field_name)

                if old_val != new_val:
                    changes[field_name] = {
                        "old": str(old_val),
                        "new": str(new_val)
                    }
            except Exception:
                continue
        return changes