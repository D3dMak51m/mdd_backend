# Procfile

web: uvicorn mdd_backend.asgi:application --host 0.0.0.0 --port $PORT
worker: celery -A mdd_backend worker -l info
beat: celery -A mdd_backend beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler