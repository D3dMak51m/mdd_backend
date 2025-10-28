# tests/integration/test_sos_pipeline.py

from unittest.mock import patch
from django.contrib.gis.geos import Point
from django.utils import timezone
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from apps.users.models import User
from apps.devices.models import Device
from apps.sos.models import SOSEvent


class SOSPipelineIntegrationTest(APITestCase):
    """
    Интеграционный тест для полного цикла обработки SOS-сигнала.
    """

    def setUp(self):
        # Создаем пользователя, который отправит SOS
        self.user_sos = User.objects.create_user(
            phone_number='+998900000001',
            full_name='User SOS',
            password='password123'
        )
        # Создаем пользователя-помощника
        self.user_helper = User.objects.create_user(
            phone_number='+998900000002',
            full_name='User Helper',
            password='password123'
        )
        self.client.force_authenticate(user=self.user_sos)

        # Регистрируем устройство для SOS
        self.device_sos = Device.objects.create(
            owner=self.user_sos,
            device_uid='sos_device_001',
            model='SOS_T1'
        )

        # Регистрируем устройство для помощника и задаем ему координаты
        self.device_helper = Device.objects.create(
            owner=self.user_helper,
            device_uid='helper_device_001',
            model='HLP_T1',
            is_online=True,
            last_latlon=Point(69.240600, 41.311100, srid=4326)  # Рядом с точкой SOS
        )

    @patch('apps.sos.tasks.notify_nearby_helpers.delay')
    def test_full_sos_trigger_flow(self, mock_notify_task):
        """
        Тестирует полный сценарий: отправка SOS -> создание события -> вызов задачи Celery.
        """
        # 1. Формируем данные для SOS-сигнала
        sos_data = {
            "device_uid": self.device_sos.device_uid,
            "lat": 41.311081,
            "lon": 69.240562,
            "detected_type": "MANUAL_TRIGGER",
            "severity": 5,
            "timestamp": timezone.now().isoformat(),
            "raw_payload": {"test": "data"}
        }

        # 2. Отправляем запрос на эндпоинт /api/v1/sos/trigger/
        url = reverse('sos-trigger')
        response = self.client.post(url, sos_data, format='json')

        # 3. Проверяем успешный ответ
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], 'created')
        self.assertIn('event_uid', response.data)

        # 4. Проверяем, что событие создано в базе данных
        self.assertEqual(SOSEvent.objects.count(), 1)
        sos_event = SOSEvent.objects.first()
        self.assertEqual(sos_event.device, self.device_sos)
        self.assertEqual(sos_event.severity, 5)

        # 5. Проверяем, что фоновая задача была вызвана с правильным ID
        mock_notify_task.assert_called_once_with(sos_event.id)