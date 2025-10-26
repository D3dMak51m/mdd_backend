# Использовать официальный образ Python
FROM python:3.12-slim

# Установить переменные окружения
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Установить рабочую директорию
WORKDIR /app

# Установить системные зависимости для psycopg2
RUN apt-get update && apt-get install -y gcc libpq-dev

# Установить зависимости Python
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Скопировать проект
COPY . /app/