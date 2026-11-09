from django.db.models import Count, Avg, Case, DurationField, F, Q, When
from django.utils import timezone
from apps.sos.models import SOSEvent
from .models import DailyIncidentStats


class AnalyticsService:
    @staticmethod
    def calculate_stats_for_day(target_date):
        """
        Считает статистику за конкретный день и сохраняет в DailyIncidentStats.
        """
        # Фильтр по дате (учитываем часовые пояса, если нужно, но пока берем date)
        events = SOSEvent.objects.filter(timestamp__date=target_date)

        # 1. Базовые счетчики
        aggregates = events.aggregate(
            total=Count('id'),
            # Support both fields because older/test records may have only one set.
            resolved=Count(
                'id',
                filter=Q(resolved=True) | Q(status=SOSEvent.Status.RESOLVED)
            ),
            # Response time: incident creation -> dispatcher acceptance.
            # For events resolved without acceptance, use creation -> resolution.
            # Ignore negative durations caused by imported/backdated test records.
            avg_time=Avg(
                Case(
                    When(
                        accepted_at__isnull=False,
                        accepted_at__gte=F('created_at'),
                        then=F('accepted_at') - F('created_at')
                    ),
                    When(
                        accepted_at__isnull=True,
                        resolved_at__isnull=False,
                        resolved_at__gte=F('created_at'),
                        then=F('resolved_at') - F('created_at')
                    ),
                    output_field=DurationField()
                )
            )
        )

        # 2. Распределение по типам
        type_dist_qs = events.values('detected_type').annotate(count=Count('id'))
        type_distribution = {item['detected_type']: item['count'] for item in type_dist_qs}

        # 3. Сохранение (Update or Create)
        stats, created = DailyIncidentStats.objects.update_or_create(
            date=target_date,
            defaults={
                'total_incidents': aggregates['total'] or 0,
                'resolved_count': aggregates['resolved'] or 0,
                'avg_response_time_seconds': aggregates['avg_time'].total_seconds() if aggregates['avg_time'] else 0.0,
                'type_distribution': type_distribution
            }
        )
        return stats

    @staticmethod
    def recalculate_last_week():
        """
        Пересчитывает данные за последние 7 дней (на случай изменений задним числом)
        """
        today = timezone.now().date()
        for i in range(8):  # Сегодня + 7 дней назад
            date = today - timezone.timedelta(days=i)
            AnalyticsService.calculate_stats_for_day(date)