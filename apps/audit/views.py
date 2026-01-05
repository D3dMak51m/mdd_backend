from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django_filters.rest_framework import DjangoFilterBackend

from .models import AuditLog
from .serializers import AuditLogSerializer


class AuditViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Журнал действий системы. Только чтение.
    """
    queryset = AuditLog.objects.select_related('actor').all()
    serializer_class = AuditLogSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['action', 'target_model']
    search_fields = ['target_str', 'actor__full_name', 'actor__phone_number']
    ordering_fields = ['created_at']
    ordering = ['-created_at']