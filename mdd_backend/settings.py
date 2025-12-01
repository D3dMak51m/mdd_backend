# mdd_backend/settings.py

import os
from pathlib import Path
import environ
from datetime import timedelta
from django.templatetags.static import static
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

# Инициализация django-environ
env = environ.Env(
    DEBUG=(bool, False)
)

# Определение базовой директории проекта
BASE_DIR = Path(__file__).resolve().parent.parent

# Чтение файла .env
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

# Настройки безопасности
SECRET_KEY = env('DJANGO_SECRET_KEY')
DEBUG = env('DEBUG')
# ALLOWED_HOSTS = env.list('DJANGO_ALLOWED_HOSTS', default=['localhost', '127.0.0.1', '10.0.2.2', '192.168.1.2', '*', '192.168.1.6'])

ALLOWED_HOSTS = ["*"]
CSRF_TRUSTED_ORIGINS = [
    "http://localhost",
    "http://127.0.0.1",
    "http://10.0.2.2",
    "http://192.168.1.2",
    "http://192.168.1.6",
]

# Приложения
INSTALLED_APPS = [

    # Django-unfold
    "unfold",
    "unfold.contrib.filters",
    "unfold.contrib.forms",

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.gis',  # GeoDjango

    # Сторонние приложения
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'drf_yasg',
    'channels',
    'django_celery_beat',
    'django_prometheus',

    # Наши приложения
    'apps.users',
    'apps.devices',
    'apps.sos',
    'apps.notifications',
    'apps.monitoring',
]

UNFOLD = {
    "SITE_TITLE": "MDD Dispatcher",
    "SITE_HEADER": "MDD Platform",
    "SITE_URL": "/",

    # Принудительно подключаем стили и скрипты
    "STYLES": [
        lambda request: static("css/admin_custom.css"),
    ],
    "SCRIPTS": [
        lambda request: static("js/admin_custom.js"),
    ],

    # Цветовая палитра (Slate - профессиональный серый/синий)
    # Это решит проблему с контрастом
    "COLORS": {
        "primary": {
            "50": "248 250 252",
            "100": "241 245 249",
            "200": "226 232 240",
            "300": "203 213 225",
            "400": "148 163 184",
            "500": "100 116 139",
            "600": "71 85 105",
            "700": "51 65 85",
            "800": "30 41 59",
            "900": "15 23 42",
            "950": "2 6 23",
        },
    },

    # Настройка сайдбара (оставляем как было, но проверяем пути)
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": False,
        "navigation": [
            {
                "title": "Оперативный центр",
                "separator": True,
                "items": [
                    {
                        "title": "Главный Дашборд",
                        "icon": "dashboard",
                        "link": reverse_lazy("admin:index"),
                    },
                    {
                        "title": "Мониторинг (Live)",
                        "icon": "public",
                        "link": reverse_lazy("live-monitor"),
                    },
                ],
            },
            {
                "title": "Управление",
                "separator": True,
                "items": [
                    {
                        "title": "SOS Сигналы",
                        "icon": "notifications_active",
                        "link": reverse_lazy("admin:sos_sosevent_changelist"),
                        "badge": "apps.monitoring.dashboard.badge_active_sos",
                    },
                    {
                        "title": "Устройства",
                        "icon": "watch",
                        "link": reverse_lazy("admin:devices_device_changelist"),
                    },
                    {
                        "title": "Пользователи",
                        "icon": "people",
                        "link": reverse_lazy("admin:users_user_changelist"),
                    },
                ],
            },
        ],
    },

    "DASHBOARD_CALLBACK": "apps.monitoring.dashboard.dashboard_callback",
}

MIDDLEWARE = [
    'django_prometheus.middleware.PrometheusBeforeMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_prometheus.middleware.PrometheusAfterMiddleware',
]

ROOT_URLCONF = 'mdd_backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# Указываем нашу кастомную модель пользователя
AUTH_USER_MODEL = 'users.User'

# WSGI и ASGI
WSGI_APPLICATION = 'mdd_backend.wsgi.application'
ASGI_APPLICATION = 'mdd_backend.asgi.application'

# База данных (PostGIS)
DATABASES = {
    'default': env.db_url('DATABASE_URL', default='postgis://postgres:postgres@db:5432/mdd_db')
}
DATABASES['default']['ENGINE'] = 'django.contrib.gis.db.backends.postgis'

# Валидаторы паролей
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Интернационализация
LANGUAGE_CODE = 'ru-ru'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Статические файлы
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

# Тип первичного ключа по умолчанию
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Django REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/day',
        'user': '1000/day'
    }
}

# Simple JWT
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
}

# CORS
CORS_ALLOW_ORIGINS = []  # Для разработки. В продакшене заменить на CORS_ALLOWED_ORIGINS
CORS_ALLOW_CREDENTIALS = True

# Celery
CELERY_BROKER_URL = env('CELERY_BROKER_URL', default='redis://redis:6379/0')
CELERY_RESULT_BACKEND = env('CELERY_BROKER_URL')  # Можно использовать тот же Redis
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'

# Channels
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [env('CACHE_URL', default='redis://redis:6379/1')],
        },
    },
}

# Sentry
SENTRY_DSN = env('SENTRY_DSN', default=None)
if SENTRY_DSN:
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration
    from sentry_sdk.integrations.celery import CeleryIntegration

    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[DjangoIntegration(), CeleryIntegration()],
        traces_sample_rate=1.0,
        send_default_pii=True
    )

    import firebase_admin
    from firebase_admin import credentials
    import json

    FCM_SERVICE_ACCOUNT_JSON = env('FCM_SERVICE_ACCOUNT_JSON', default=None)

    if FCM_SERVICE_ACCOUNT_JSON and not firebase_admin._apps:
        try:
            # Если переменная содержит путь к файлу
            if os.path.exists(FCM_SERVICE_ACCOUNT_JSON):
                cred = credentials.Certificate(FCM_SERVICE_ACCOUNT_JSON)
            else:
                # Если переменная содержит JSON-строку
                cred_json = json.loads(FCM_SERVICE_ACCOUNT_JSON)
                cred = credentials.Certificate(cred_json)

            firebase_admin.initialize_app(cred)
            print("Firebase Admin SDK инициализирован успешно.")
        except Exception as e:
            print(f"Ошибка инициализации Firebase Admin SDK: {e}")

# Настройка для drf-yasg для подавления DeprecationWarning
SWAGGER_SETTINGS = {
    'USE_SESSION_AUTH': False,
    'SECURITY_DEFINITIONS': {
        'Bearer': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header',
            'description': 'Введите "Bearer {токен}"'
        }
    }
}
