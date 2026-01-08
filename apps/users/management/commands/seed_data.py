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
    help = 'Заполняет БД тестовыми данными для Ташкента (с историей и статусами)'

    def handle(self, *args, **kwargs):
        self.stdout.write("🧹 Очистка старых данных (Треки и События)...")
        LocationTrack.objects.all().delete()
        SOSEvent.objects.all().delete()

        self.stdout.write("🚀 Начинаем генерацию данных...")

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

        self.stdout.write(f"✅ Пользователи: {len(users)} шт.")

        # 2. Создание устройств
        devices = []
        device_models = ["Galaxy Watch 4", "Apple Watch 7", "Xiaomi Band 8", "Garmin Fenix"]

        for i, user in enumerate(users):
            is_online = random.choice([True, True, False])

            # Если онлайн - последнее обновление прямо сейчас, если нет - от 1 до 10 часов назад
            last_update_time = timezone.now() if is_online else timezone.now() - timedelta(hours=random.randint(1, 10))

            device, created = Device.objects.update_or_create(
                device_uid=f"device_{user.phone_number}",
                defaults={
                    'owner': user,
                    'model': random.choice(device_models),
                    'battery_level': random.randint(20, 100),
                    'is_online': is_online,
                    'last_seen_via': 'LTE',
                    'last_update': last_update_time  # <-- ВАЖНО: Заполняем время обновления
                }
            )

            # Генерируем случайную точку в Ташкенте
            lat = TASHKENT_LAT + random.uniform(-0.05, 0.05)
            lon = TASHKENT_LON + random.uniform(-0.06, 0.06)
            device.last_latlon = Point(lon, lat, srid=4326)
            device.save()
            devices.append(device)

        self.stdout.write(f"✅ Устройства: {len(devices)} шт.")

        # 3. Генерация треков (история за 30 дней)
        self.stdout.write("⏳ Генерация истории перемещений...")
        tracks_to_create = []
        now = timezone.now()

        for device in devices:
            current_lat = device.last_latlon.y
            current_lon = device.last_latlon.x

            # Генерируем 30 точек (по 1 на день назад)
            for day in range(30):
                # Двигаемся назад во времени и пространстве
                current_lat -= random.uniform(-0.002, 0.002)
                current_lon -= random.uniform(-0.002, 0.002)

                track_time = now - timedelta(days=day)

                tracks_to_create.append(LocationTrack(
                    device=device,
                    latlon=Point(current_lon, current_lat, srid=4326),
                    speed=random.uniform(0, 5),
                    direction=random.uniform(0, 360),
                    battery_level=random.randint(10, 100),
                    created_at=track_time
                ))

        LocationTrack.objects.bulk_create(tracks_to_create)
        self.stdout.write(f"✅ Треки: {len(tracks_to_create)} точек.")

        # 4. Создание SOS событий
        sos_events = []

        # А) АРХИВНЫЕ (Решенные) - 15 штук
        for _ in range(15):
            device = random.choice(devices)
            # Случилось от 1 до 20 дней назад
            event_time = now - timedelta(days=random.randint(1, 20), hours=random.randint(0, 23))

            # Решено через 15-60 минут после создания
            resolve_time = event_time + timedelta(minutes=random.randint(15, 60))

            # Кто решил (случайный пользователь, кроме пострадавшего)
            potential_resolvers = [u for u in users if u != device.owner]
            resolver = random.choice(potential_resolvers) if potential_resolvers else users[0]

            lat = device.last_latlon.y + random.uniform(-0.001, 0.001)
            lon = device.last_latlon.x + random.uniform(-0.001, 0.001)

            sos_events.append(SOSEvent(
                device=device,
                user=device.owner,
                latlon=Point(lon, lat, srid=4326),
                detected_type=random.choice(SOSEvent.DetectedType.values),
                severity=random.randint(1, 5),
                timestamp=event_time,

                # --- ЗАПОЛНЯЕМ ПОЛЯ РЕШЕНИЯ ---
                status=SOSEvent.Status.RESOLVED,
                resolved=True,
                resolved_by=resolver,  # <-- Кто решил
                resolved_at=resolve_time,  # <-- Когда решил
                accepted_by=resolver,  # <-- Он же и принял
                accepted_at=event_time + timedelta(minutes=5),  # <-- Принял через 5 мин

                dedup_hash=f"old_{random.randint(10000, 99999)}",
                raw_payload={"info": "Test archive data"}
            ))

        # Б) АКТИВНЫЕ (Новые) - 3 штуки
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
                timestamp=now - timedelta(minutes=random.randint(1, 10)),

                # --- АКТИВНЫЕ ПОЛЯ ---
                status=SOSEvent.Status.NEW,
                resolved=False,
                resolved_at=None,
                resolved_by=None,

                dedup_hash=f"new_{random.randint(10000, 99999)}",
                raw_payload={"info": "Realtime test data"}
            ))

        SOSEvent.objects.bulk_create(sos_events)
        self.stdout.write(f"✅ SOS-события: {len(sos_events)} (3 активных, 15 архивных).")

        self.stdout.write(self.style.SUCCESS("🎉 База данных успешно обновлена!"))