from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from apps.analytics.services import AnalyticsService


class Command(BaseCommand):
    help = 'Пересчитывает статистику за последние N дней'

    def add_arguments(self, parser):
        parser.add_argument('--days', type=int, default=30, help='Количество дней для пересчета')

    def handle(self, *args, **options):
        days = options['days']
        self.stdout.write(f"Начинаем пересчет статистики за последние {days} дней...")

        today = timezone.now().date()

        for i in range(days):
            target_date = today - timedelta(days=i)
            self.stdout.write(f"Обработка: {target_date}...", ending='')

            stats = AnalyticsService.calculate_stats_for_day(target_date)

            self.stdout.write(self.style.SUCCESS(f" OK (Инцидентов: {stats.total_incidents})"))

        self.stdout.write(self.style.SUCCESS("Готово!"))