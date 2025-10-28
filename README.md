# MDD Backend: Серверная часть проекта

Это бэкенд-сервис для проекта MDD. Его основная задача — регистрация пользователей и носимых устройств (часов), прием и обработка экстренных SOS-сигналов, и мгновенное оповещение ближайших помощников о необходимости оказать помощь.

## Оглавление

1.  [Цель проекта](#1-цель-проекта)
2.  [Архитектура и основной флоу](#2-архитектура-и-основной-флоу)
3.  [Технологический стек](#3-технологический-стек)
4.  [Настройка окружения для разработки](#4-настройка-окружения-для-разработки-быстрый-старт)
5.  [Основные команды для разработки](#5-основные-команды-для-разработки)
6.  [Справочник по API для мобильных разработчиков](#6-справочник-по-api-для-мобильных-разработчиков)
    *   [6.1 Аутентификация](#61-аутентификация)
    *   [6.2 Устройства (Devices)](#62-устройства-devices)
    *   [6.3 SOS-события](#63-sos-события)
7.  [Real-time оповещения (WebSockets)](#7-real-time-оповещения-websockets)
8.  [Руководство по развертыванию (Production)](#8-руководство-по-развертыванию-production)
9.  [Резервное копирование и восстановление](#9-резервное-копирование-и-восстановление)
10. [Структура проекта](#10-структура-проекта)

---

## 1. Цель проекта

Система предназначена для обеспечения безопасности пользователей носимых устройств. В случае экстренной ситуации (падение, нажатие кнопки SOS) устройство отправляет сигнал на сервер. Сервер определяет местоположение пользователя, находит ближайших зарегистрированных помощников в заданном радиусе и рассылает им push-уведомления с призывом о помощи.

---

## 2. Архитектура и основной флоу

Система построена на микросервисной архитектуре, управляемой через Docker Compose.

**Основной флоу обработки SOS-сигнала:**
1.  **Прием:** Устройство или мобильное приложение отправляет POST-запрос на эндпоинт `/api/v1/sos/trigger/`.
2.  **Валидация и дедупликация:** Сервер проверяет данные и вычисляет хэш для предотвращения обработки дублирующихся сигналов в короткий промежуток времени.
3.  **Сохранение:** В базе данных создается запись о новом SOS-событии.
4.  **Запуск фоновых задач:**
    *   Немедленно запускается задача Celery `notify_nearby_helpers`.
    *   Эта задача делает запрос к базе данных PostGIS, чтобы найти ближайших онлайн-помощников.
    *   Для каждого найденного помощника создается запись в логе уведомлений и запускается задача отправки push-уведомления через FCM.
5.  **Real-time оповещение:** Одновременно с шагом 4, сервер отправляет сообщение через WebSocket всем подключенным администраторам (диспетчерам) для мгновенного отображения события на карте.
6.  **Эскалация:** Запускается отложенная задача Celery `escalation_watch`, которая через несколько минут проверит, было ли событие взято в работу.

---

## 3. Технологический стек

*   **Ядро:** Django 5.2 (ASGI)
*   **REST API:** Django REST Framework (DRF)
*   **Аутентификация:** JWT (djangorestframework-simplejwt)
*   **База данных:** PostgreSQL 16 + PostGIS
*   **Кэш / Брокер задач:** Redis
*   **Фоновые задачи:** Celery (worker + beat)
*   **Real-time:** Django Channels (WebSocket)
*   **Push-уведомления:** Firebase Cloud Messaging (FCM)
*   **Документация API:** OpenAPI (drf-yasg)
*   **Контейнеризация:** Docker + Docker Compose
*   **Веб-сервер:** NGINX + Uvicorn

---

## 4. Настройка окружения для разработки (Быстрый старт)

### Требования

*   Docker
*   Docker Compose

### Установка и запуск

1.  **Клонируйте репозиторий:**
    ```bash
    git clone <URL_этого_репозитория>
    cd mdd_backend
    ```

2.  **Создайте и настройте файл окружения:**
    Скопируйте `.env.example` в `.env` и заполните необходимые переменные.
    ```bash
    cp .env.example .env
    ```
    *   `DJANGO_SECRET_KEY`: **Обязательно.** Сгенерируйте секретный ключ (например, с помощью `python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'`).
    *   `SENTRY_DSN`: (Опционально) Укажите DSN из вашего проекта Sentry для отслеживания ошибок.
    *   `FCM_SERVICE_ACCOUNT_JSON`: (Опционально) Вставьте содержимое JSON-ключа сервисного аккаунта Firebase в одну строку. Без этого не будут работать push-уведомления.

3.  **Соберите и запустите контейнеры:**
    Эта команда соберет Docker-образы и запустит все сервисы в фоновом режиме.
    ```bash
    docker-compose up --build -d
    ```

4.  **Примените миграции базы данных:**
    Это создаст все необходимые таблицы в базе данных.
    ```bash
    docker-compose exec web python manage.py migrate
    ```

5.  **Создайте суперпользователя:**
    Этот пользователь понадобится для доступа к админ-панели (`/admin/`).
    ```bash
    docker-compose exec web python manage.py createsuperuser
    ```

6.  **Соберите статические файлы:**
    Это необходимо, чтобы Nginx мог корректно отображать CSS и JS админ-панели.
    ```bash
    docker-compose exec web python manage.py collectstatic --no-input
    ```

После выполнения этих шагов приложение будет доступно по адресу `http://localhost`.

---

## 5. Основные команды для разработки

*   **Запуск тестов:**
    ```bash
    docker-compose exec web pytest
    ```
*   **Создание миграций после изменения моделей:**
    ```bash
    docker-compose exec web python manage.py makemigrations <имя_приложения>
    ```
*   **Применение миграций:**
    ```bash
    docker-compose exec web python manage.py migrate
    ```
*   **Запуск Django shell для работы с ORM:**
    ```bash
    docker-compose exec web python manage.py shell
    ```
*   **Просмотр логов в реальном времени:**
    ```bash
    docker-compose logs -f web worker beat
    ```

---

## 6. Справочник по API для мобильных разработчиков

**Базовый URL API:** `http://localhost/api/v1/`

**Аутентификация:** Все защищенные эндпоинты требуют заголовок `Authorization: Bearer <access_token>`.

### 6.1 Аутентификация

#### Регистрация
*   **URL:** `/auth/register/`
*   **Метод:** `POST`
*   **Аутентификация:** Не требуется.
*   **Тело запроса:**
    ```json
    {
        "phone_number": "+998901234567",
        "full_name": "Full Name",
        "password": "someStrongPassword123",
        "password2": "someStrongPassword123"
    }
    ```
*   **Успешный ответ (201 Created):**
    ```json
    {
        "user": {
            "uuid": "...",
            "full_name": "Full Name",
            "phone_number": "+998901234567",
            "email": null,
            "role": "USER",
            "status": "ACTIVE"
        },
        "access": "...",
        "refresh": "..."
    }
    ```

#### Получение токена (Вход)
*   **URL:** `/auth/login/`
*   **Метод:** `POST`
*   **Аутентификация:** Не требуется.
*   **Тело запроса:**
    ```json
    {
        "phone_number": "+998901234567",
        "password": "someStrongPassword123"
    }
    ```
*   **Успешный ответ (200 OK):**
    ```json
    {
        "access": "...",
        "refresh": "..."
    }
    ```

#### Обновление токена
*   **URL:** `/auth/refresh/`
*   **Метод:** `POST`
*   **Аутентификация:** Не требуется.
*   **Тело запроса:**
    ```json
    {
        "refresh": "ВАШ_REFRESH_ТОКЕН"
    }
    ```
*   **Успешный ответ (200 OK):**
    ```json
    {
        "access": "НОВЫЙ_ACCESS_ТОКЕН"
    }
    ```

### 6.2 Устройства (Devices)

#### Регистрация устройства
*   **URL:** `/devices/`
*   **Метод:** `POST`
*   **Аутентификация:** Требуется (Bearer Token). Владельцем устройства станет пользователь из токена.
*   **Тело запроса:**
    ```json
    {
        "device_uid": "watch_unique_serial_001",
        "model": "T-Watch 5"
    }
    ```
*   **Успешный ответ (201 Created):**
    ```json
    {
        "uuid": "...",
        "device_uid": "watch_unique_serial_001",
        "model": "T-Watch 5",
        "sim_number": null
    }
    ```

#### Обновление статуса устройства
*   **URL:** `/devices/{device_uid}/status/`
*   **Метод:** `PATCH`
*   **Аутентификация:** Требуется (Bearer Token).
*   **Тело запроса (все поля опциональны):**
    ```json
    {
        "battery_level": 85,
        "is_online": true,
        "lat": 41.311081,
        "lon": 69.240562,
        "last_seen_via": "LTE"
    }
    ```
*   **Успешный ответ (200 OK):** Возвращает полный объект устройства с обновленными данными.

#### Запись трека местоположения
*   **URL:** `/devices/{device_uid}/location/`
*   **Метод:** `POST`
*   **Аутентификация:** Требуется (Bearer Token).
*   **Тело запроса:**
    ```json
    {
        "lat": 41.311081,
        "lon": 69.240562,
        "speed": 5.5,
        "direction": 180.0,
        "battery_level": 84
    }
    ```
*   **Успешный ответ (201 Created):**
    ```json
    {
        "status": "location recorded"
    }
    ```

### 6.3 SOS-события

#### Отправка SOS-сигнала
*   **URL:** `/sos/trigger/`
*   **Метод:** `POST`
*   **Аутентификация:** Требуется (Bearer Token).
*   **Тело запроса:**
    ```json
    {
        "device_uid": "watch_unique_serial_001",
        "lat": 41.311081,
        "lon": 69.240562,
        "altitude": 500.0,
        "detected_type": "FALL_DETECTED",
        "severity": 4,
        "timestamp": "2025-10-28T12:00:00Z",
        "raw_payload": { "sensor_data": "..." }
    }
    ```
*   **Успешный ответ (201 Created):**
    ```json
    {
        "status": "created",
        "event_uid": "..."
    }
    ```
*   **Ответ при дубликате (200 OK):**
    ```json
    {
        "status": "duplicate",
        "event_uid": "..."
    }
    ```

---

## 7. Real-time оповещения (WebSockets)

Система использует Django Channels для отправки уведомлений о новых SOS-событиях в реальном времени.

*   **URL для подключения:** `ws://localhost/ws/sos_events/`
*   **Аутентификация:** Требуется. Клиент должен передать заголовок `Authorization: Bearer <admin_access_token>`. Доступ разрешен только пользователям с ролью `ADMIN`.
*   **Формат сообщения от сервера:** При создании нового SOS-события сервер отправит JSON-сообщение следующего вида:
    ```json
    {
        "type": "sos_event",
        "payload": {
            "event_uid": "...",
            "timestamp": "2025-10-28T12:00:00Z",
            "resolved": false,
            "detected_type": "FALL_DETECTED",
            "severity": 4,
            "device_uid": "watch_unique_serial_001",
            "user_phone": "+998901234567",
            "lat": 41.311081,
            "lon": 69.240562
        }
    }
    ```

---

## 8. Руководство по развертыванию (Production)

Для развертывания проекта в продакшен-среде рекомендуется использовать `docker-compose.prod.yml` (необходимо создать) и переменные окружения, оптимизированные для безопасности и производительности.

**Основные отличия от dev-окружения:**
*   `DEBUG` должен быть установлен в `False`.
*   `DJANGO_SECRET_KEY` должен быть уникальным и храниться в секрете.
*   `DJANGO_ALLOWED_HOSTS` должен содержать доменное имя вашего сервера.
*   `CORS_ALLOW_ALL_ORIGINS` должен быть `False`, вместо него используется `CORS_ALLOWED_ORIGINS`.
*   Исходный код не монтируется в контейнер, а копируется в образ на этапе сборки.

**Пример `docker-compose.prod.yml`:**
```yaml
# docker-compose.prod.yml (Пример)
services:
  db:
    # ... (конфигурация как в dev, но можно вынести пароли в Docker Secrets)
  redis:
    # ... (конфигурация как в dev)
  web:
    image: your_registry/mdd_backend:latest # Используем собранный образ
    command: uvicorn mdd_backend.asgi:application --host 0.0.0.0 --port 8000 --workers 4
    env_file: .env.prod
    depends_on:
      - db
      - redis
  # ... (worker, beat)
  nginx:
    image: nginx:1.25-alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/prod.conf:/etc/nginx/conf.d/default.conf
      # - /path/to/ssl_certs:/etc/ssl/private
      - static_volume:/app/static
    depends_on:
      - web

volumes:
  postgres_data:
  static_volume:
```

---

## 9. Резервное копирование и восстановление

### Создание бэкапа
Скрипт `scripts/backup_pg.sh` создает сжатый дамп базы данных. В продакшен-среде его следует запускать по расписанию (`cron`).
```bash
# Пример ручного запуска
docker-compose exec -e POSTGRES_PASSWORD=your_prod_password web sh -c "dos2unix /app/scripts/backup_pg.sh && /app/scripts/backup_pg.sh"```

### Восстановление из бэкапа
**ВНИМАНИЕ: Эта команда перезапишет существующие данные в базе.**
```bash
docker-compose exec -T web sh -c "gunzip < /backups/имя_файла.sql.gz" | docker-compose exec -T db psql -U postgres -d mdd_db
```

---

## 10. Структура проекта

```
mdd_backend/
├── .github/workflows/ci.yml  # CI для GitHub Actions
├── apps/                     # Директория с приложениями Django
│   ├── devices/
│   ├── monitoring/
│   ├── notifications/
│   ├── sos/
│   └── users/
├── mdd_backend/              # Ядро проекта Django (settings, urls)
├── nginx/                    # Конфигурации Nginx (dev.conf, prod.conf)
├── scripts/                  # Вспомогательные скрипты (бэкап)
├── tests/                    # Тесты
├── .env.example              # Шаблон переменных окружения
├── .gitattributes            # Настройки Git для окончаний строк
├── docker-compose.yml        # Конфигурация Docker Compose для разработки
├── Dockerfile                # Dockerfile для сборки приложения
├── pytest.ini                # Конфигурация Pytest
├── requirements.txt          # Зависимости для продакшена
├── requirements-dev.txt      # Зависимости для разработки
└── README.md                 # Этот файл
```