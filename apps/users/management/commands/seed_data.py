import random
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.gis.geos import Point
from django.contrib.auth import get_user_model
from apps.devices.models import Device, LocationTrack
from apps.sos.models import SOSEvent

User = get_user_model()

# Центр Ташкента
TASHKENT_LAT = 41.311081
TASHKENT_LON = 69.240562


class Command(BaseCommand):
    help = 'Заполняет БД тестовыми данными для Ташкента (2025 год)'

    def handle(self, *args, **kwargs):
        self.stdout.write("Начинаем генерацию данных...")

        # 1. Создание пользователей
        users = []
        for i in range(10):
            # Генерация номера: +998 90 1234567, 91, 92...
            phone = f"+998{90 + i}1234567"
            role = User.Role.HELPER if i > 2 else User.Role.USER

            user, created = User.objects.get_or_create(
                phone_number=phone,
                defaults={
                    'full_name': f"Test User {i}",
                    'role': role,
                    'is_active': True,
                    'fcm_token': f"fake_token_{i}"
                }
            )
            if created:
                user.set_password("1234")
                user.save()
            users.append(user)

        self.stdout.write(f"✅ Создано/Обновлено {len(users)} пользователей.")

        # 2. Создание устройств
        devices = []
        device_models = ["Galaxy Watch 4", "Apple Watch 7", "Xiaomi Band 8"]

        for i, user in enumerate(users):
            device, created = Device.objects.get_or_create(
                device_uid=f"device_{user.phone_number}",
                defaults={
                    'owner': user,
                    'model': random.choice(device_models),
                    'battery_level': random.randint(20, 100),
                    'is_online': random.choice([True, True, False]),  # Чаще онлайн
                    'last_seen_via': 'LTE'
                }
            )

            # Генерируем случайную точку в Ташкенте (разброс ~5-10 км)
            lat = TASHKENT_LAT + random.uniform(-0.05, 0.05)
            lon = TASHKENT_LON + random.uniform(-0.06, 0.06)
            device.last_latlon = Point(lon, lat, srid=4326)
            device.save()
            devices.append(device)

        self.stdout.write(f"✅ Создано/Обновлено {len(devices)} устройств.")

        # 3. Генерация треков (история за 30 дней)
        self.stdout.write("⏳ Генерация истории перемещений (это может занять пару секунд)...")
        tracks_to_create = []
        now = timezone.now()

        for device in devices:
            # Для каждого устройства генерируем путь
            # Начальная точка (где-то в Ташкенте)
            current_lat = TASHKENT_LAT + random.uniform(-0.04, 0.04)
            current_lon = TASHKENT_LON + random.uniform(-0.05, 0.05)

            # Генерируем 50 точек за последний месяц
            for day in range(30):
                # Небольшое смещение (имитация ходьбы/езды)
                current_lat += random.uniform(-0.002, 0.002)
                current_lon += random.uniform(-0.002, 0.002)

                track_time = now - timedelta(days=day)

                tracks_to_create.append(LocationTrack(
                    device=device,
                    latlon=Point(current_lon, current_lat, srid=4326),
                    speed=random.uniform(0, 60),
                    battery_level=random.randint(10, 100),
                    created_at=track_time
                    # Внимание: auto_now_add может перезаписать это при save, но bulk_create работает
                ))

        # bulk_create игнорирует auto_now_add, поэтому created_at сохранится как мы задали
        LocationTrack.objects.bulk_create(tracks_to_create)
        self.stdout.write(f"✅ Создано {len(tracks_to_create)} точек трекинга.")

        # 4. Создание SOS событий (Архив и Активные)
        sos_events = []

        # А) Архивные (решенные)
        for _ in range(15):
            device = random.choice(devices)
            event_time = now - timedelta(days=random.randint(1, 20))

            # Координаты события (где-то рядом с устройством)
            lat = device.last_latlon.y + random.uniform(-0.001, 0.001)
            lon = device.last_latlon.x + random.uniform(-0.001, 0.001)

            sos_events.append(SOSEvent(
                device=device,
                user=device.owner,
                latlon=Point(lon, lat, srid=4326),
                detected_type=random.choice(SOSEvent.DetectedType.values),
                severity=random.randint(1, 5),
                timestamp=event_time,
                resolved=True,
                status=SOSEvent.Status.RESOLVED,
                dedup_hash=f"old_{random.randint(1000, 9999)}"
            ))

        # Б) АКТИВНЫЕ (Прямо сейчас!) - 3 штуки
        active_devices = random.sample(devices, 3)
        for i, device in enumerate(active_devices):
            lat = TASHKENT_LAT + random.uniform(-0.02, 0.02)
            lon = TASHKENT_LON + random.uniform(-0.03, 0.03)

            sos_events.append(SOSEvent(
                device=device,
                user=device.owner,
                latlon=Point(lon, lat, srid=4326),
                detected_type=SOSEvent.DetectedType.FALL if i % 2 == 0 else SOSEvent.DetectedType.MANUAL,
                severity=5,
                timestamp=now - timedelta(minutes=random.randint(1, 10)),  # Случилось 1-10 мин назад
                resolved=False,
                status=SOSEvent.Status.NEW,
                dedup_hash=f"new_{random.randint(1000, 9999)}"
            ))

        SOSEvent.objects.bulk_create(sos_events)
        self.stdout.write(f"✅ Создано {len(sos_events)} SOS-событий (3 активных).")

        self.stdout.write(self.style.SUCCESS("🎉 База данных успешно заполнена!"))