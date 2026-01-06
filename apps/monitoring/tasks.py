# apps/monitoring/tasks.py
from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from apps.devices.models import LocationTrack
from apps.sos.models import SOSEvent


@shared_task
def cleanup_old_data():
    """
    Удаляет старые треки и логи, чтобы не засорять БД.
    Запускается раз в сутки.
    """
    # 1. Удаляем треки старше 30 дней
    track_threshold = timezone.now() - timedelta(days=30)
    deleted_tracks, _ = LocationTrack.objects.filter(created_at__lt=track_threshold).delete()

    # 2. (Опционально) Удаляем решенные SOS старше 1 года
    sos_threshold = timezone.now() - timedelta(days=365)
    deleted_sos, _ = SOSEvent.objects.filter(
        created_at__lt=sos_threshold,
        status=SOSEvent.Status.RESOLVED
    ).delete()

    return f"Cleanup: Deleted {deleted_tracks} tracks, {deleted_sos} old SOS events."