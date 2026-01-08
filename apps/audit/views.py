from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.pagination import PageNumberPagination  # <-- Импорт
from django_filters.rest_framework import DjangoFilterBackend

from .models import AuditLog
from .serializers import AuditLogSerializer


# Создаем класс пагинации
class StandardResultsSetPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class AuditViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Журнал действий системы. Только чтение.
    """
    queryset = AuditLog.objects.select_related('actor').all()
    serializer_class = AuditLogSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

    # Подключаем пагинацию
    pagination_class = StandardResultsSetPagination

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    # Добавили target_id в фильтры (нужно для истории в карточке инцидента)
    filterset_fields = ['action', 'target_model', 'target_id']
    search_fields = ['target_str', 'actor__full_name', 'actor__phone_number']
    ordering_fields = ['created_at']
    ordering = ['-created_at']