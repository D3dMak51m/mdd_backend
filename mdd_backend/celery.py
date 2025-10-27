# mdd_backend/celery.py

import os
from celery import Celery

# Установить модуль настроек Django по умолчанию для 'celery'.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mdd_backend.settings')

app = Celery('mdd_backend')

# Использовать строку конфигурации из Django.
# Пространство имен 'CELERY' означает, что все настройки Celery
# должны иметь префикс 'CELERY_'.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Автоматически обнаруживать файлы tasks.py в приложениях Django.
app.autodiscover_tasks()