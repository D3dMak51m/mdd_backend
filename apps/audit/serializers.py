from rest_framework import serializers
from .models import AuditLog

class AuditLogSerializer(serializers.ModelSerializer):
    actor_name = serializers.CharField(source='actor.full_name', read_only=True)
    actor_phone = serializers.CharField(source='actor.phone_number', read_only=True)

    class Meta:
        model = AuditLog
        fields = (
            'id', 'actor_name', 'actor_phone', 'action',
            'target_model', 'target_id', 'target_str',
            'changes', 'ip_address', 'created_at'
        )