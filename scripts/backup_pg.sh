# scripts/backup_pg.sh

#!/bin/sh

# Запретить выполнение скрипта, если какая-либо команда завершится с ошибкой
set -e

# Переменные окружения для подключения к БД
# Эти переменные должны быть доступны в среде, где запускается скрипт.
# В Docker Compose их можно передать из .env файла.
DB_NAME=${POSTGRES_DB:-mdd_db}
DB_USER=${POSTGRES_USER:-postgres}
DB_PASS=${POSTGRES_PASSWORD:-postgres}
DB_HOST=${POSTGRES_HOST:-db} # Имя сервиса из docker-compose.yml
DB_PORT=${POSTGRES_PORT:-5432}

# Директория для сохранения бэкапов внутри контейнера
BACKUP_DIR="/backups"
mkdir -p $BACKUP_DIR

# Формат имени файла: db_name_YYYY-MM-DD_HH-MM-SS.sql.gz
FILENAME="${DB_NAME}_$(date +%Y-%m-%d_%H-%M-%S).sql.gz"
BACKUP_FILE="${BACKUP_DIR}/${FILENAME}"

echo "Создание бэкапа базы данных '${DB_NAME}'..."

# Устанавливаем переменную PGPASSWORD, чтобы pg_dump не запрашивал пароль
export PGPASSWORD=$DB_PASS

# Команда для создания бэкапа
# pg_dump создает текстовый SQL-файл, который мы сжимаем с помощью gzip
pg_dump -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME | gzip > $BACKUP_FILE

# Убираем переменную с паролем из окружения
unset PGPASSWORD

echo "Бэкап успешно создан: ${BACKUP_FILE}"

# (Опционально) Удаление старых бэкапов (например, старше 7 дней)
# find $BACKUP_DIR -type f -name "*.sql.gz" -mtime +7 -delete
# echo "Старые бэкапы (старше 7 дней) удалены."

# (Опционально для продакшена) Загрузка в облачное хранилище
# aws s3 cp $BACKUP_FILE s3://your-backup-bucket/
# echo "Бэкап загружен в S3."