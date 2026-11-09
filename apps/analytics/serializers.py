from rest_framework import serializers
from .models import DailyIncidentStats

class DailyStatsSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyIncidentStats
        fields = '__all__'