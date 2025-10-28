# MDD Backend

Это бэкенд-сервис для проекта MDD, предназначенный для отслеживания устройств, обработки SOS-сигналов и оповещения помощников.

## Технологический стек

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

## Быстрый старт (Разработка)

### Требования

*   Docker
*   Docker Compose

### Установка и запуск

1.  **Клонируйте репозиторий:**
    ```bash
    git clone <URL_вашего_репозитория>
    cd mdd_backend
    ```

2.  **Создайте и настройте файл окружения:**
    Скопируйте `.env.example` в `.env` и заполните необходимые переменные.
    ```bash
    cp .env.example .env
    ```
    *   `DJANGO_SECRET_KEY`: Сгенерируйте секретный ключ.
    *   `SENTRY_DSN`: (Опционально) Укажите DSN из вашего проекта Sentry.
    *   `FCM_SERVICE_ACCOUNT_JSON`: (Опционально) Вставьте содержимое JSON-ключа сервисного аккаунта Firebase в одну строку.

3.  **Соберите и запустите контейнеры:**
    ```bash
    docker-compose up --build -d
    ```

4.  **Примените миграции базы данных:**
    ```bash
    docker-compose exec web python manage.py migrate
    ```

5.  **Создайте суперпользователя (для доступа к админ-панели):**
    ```bash
    docker-compose exec web python manage.py createsuperuser
    ```

6.  **Соберите статические файлы:**
    ```bash
    docker-compose exec web python manage.py collectstatic --no-input
    ```

После выполнения этих шагов приложение будет доступно по адресу `http://localhost`.

## Основные эндпоинты

*   **API:** `http://localhost/api/v1/`
*   **Админ-панель:** `http://localhost/admin/`
*   **Документация API (Swagger):** `http://localhost/swagger/`
*   **Документация API (ReDoc):** `http://localhost/redoc/`
*   **Метрики Prometheus:** `http://localhost/metrics/`
*   **WebSocket для SOS-событий:** `ws://localhost/ws/sos_events/`

## Запуск тестов

Для запуска всего набора тестов выполните команду:
```bash
docker-compose exec web pytest
```

## Резервное копирование

Для создания резервной копии базы данных выполните скрипт:
```bash
docker-compose exec -e POSTGRES_PASSWORD=postgres web sh -c "dos2unix /app/scripts/backup_pg.sh && /app/scripts/backup_pg.sh"
```
Бэкапы сохраняются в директорию `/backups` внутри `web` контейнера.

## Структура проекта

```
backend/
├── .github/workflows/ci.yml  # CI для GitHub Actions
├── apps/                     # Директория с приложениями Django
│   ├── devices/
│   ├── monitoring/
│   ├── notifications/
│   ├── sos/
│   └── users/
├── mdd_backend/              # Ядро проекта Django
├── nginx/                    # Конфигурация Nginx
├── scripts/                  # Вспомогательные скрипты (бэкап)
├── tests/                    # Тесты
├── .env.example              # Шаблон переменных окружения
├── docker-compose.yml        # Конфигурация Docker Compose
├── Dockerfile                # Dockerfile для сборки приложения
└── README.md                 # Этот файл
```

**2. Создание Postman-коллекции (инструкция)**

Создание полной Postman-коллекции — это ручной процесс, но мы можем описать, как это сделать, и предоставить примеры запросов. Эту информацию можно добавить в `README.md` или в отдельный файл `API_USAGE.md`.

**Пример запроса для Postman (можно импортировать как "Raw text"):**

**Регистрация:**
```curl
curl --location 'http://localhost/api/v1/auth/register/' \
--header 'Content-Type: application/json' \
--data '{
    "phone_number": "+998901234567",
    "full_name": "Test User",
    "password": "password123",
    "password2": "password123"
}'
```

**Вход (получение токена):**
```curl
curl --location 'http://localhost/api/v1/auth/login/' \
--header 'Content-Type: application/json' \
--data '{
    "phone_number": "+998901234567",
    "password": "password123"
}'```

**Регистрация устройства:**
```curl
curl --location 'http://localhost/api/v1/devices/' \
--header 'Authorization: Bearer ВАШ_ACCESS_ТОКЕН' \
--header 'Content-Type: application/json' \
--data '{
    "device_uid": "watch_test_001",
    "model": "T-Watch 5"
}'
```

**Отправка SOS:**
```curl
curl --location 'http://localhost/api/v1/sos/trigger/' \
--header 'Authorization: Bearer ВАШ_ACCESS_ТОКЕН' \
--header 'Content-Type: application/json' \
--data '{
    "device_uid": "watch_test_001",
    "lat": 41.311081,
    "lon": 69.240562,
    "detected_type": "MANUAL_TRIGGER",
    "severity": 4,
    "timestamp": "2025-10-28T12:00:00Z",
    "raw_payload": {}
}'
```