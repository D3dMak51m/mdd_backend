# Использовать официальный образ Python
FROM python:3.12-slim

# Аргумент для определения окружения (dev по умолчанию)
ARG APP_ENV=dev

# Установить переменные окружения
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Установить рабочую директорию
WORKDIR /app

# Установить системные зависимости для GeoDjango и psycopg2
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    binutils \
    libgdal-dev \
    gdal-bin \
    gcc \
    libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# Установить зависимости Python
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Установить dev-зависимости, если APP_ENV=dev
COPY requirements-dev.txt /app/
RUN if [ "$APP_ENV" = "dev" ]; then pip install --no-cache-dir -r requirements-dev.txt; fi

# Скопировать проект
COPY . /app/