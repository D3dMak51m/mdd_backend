from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import DailyIncidentStats
from .serializers import DailyStatsSerializer
from .services import AnalyticsService


class AnalyticsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API для получения агрегированной статистики.
    """
    queryset = DailyIncidentStats.objects.all()
    serializer_class = DailyStatsSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]  # Только для админов/диспетчеров

    def get_queryset(self):
        queryset = super().get_queryset()
        # Фильтр по диапазону дат
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')

        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)

        return queryset.order_by('date')

    @swagger_auto_schema(
        operation_summary="Получить сводку за последние 7 дней",
        responses={200: DailyStatsSerializer(many=True)}
    )
    @action(detail=False, methods=['get'])
    def weekly_summary(self, request):
        """
        Удобный метод для дашборда: возвращает данные за последние 7 дней.
        Если данных за сегодня нет, пытается их пересчитать.
        """
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=6)

        # Проверяем, есть ли статистика за сегодня, если нет - запускаем расчет
        if not DailyIncidentStats.objects.filter(date=end_date).exists():
            AnalyticsService.calculate_stats_for_day(end_date)

        queryset = self.get_queryset().filter(date__range=[start_date, end_date])
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)