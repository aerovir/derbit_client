#!/bin/bash
set -e

# Wait for PostgreSQL using Python (pg_isready not available in slim image)
echo "Waiting for PostgreSQL..."
until python3 -c "
import psycopg2
psycopg2.connect(
    host='${DB_HOST:-db}',
    port='${DB_PORT:-5432}',
    user='${DB_USER:-deribit}',
    password='${DB_PASSWORD:-deribit}',
    dbname='${DB_NAME:-deribit}'
)
" 2>/dev/null; do
    sleep 1
done
echo "PostgreSQL is ready."

# Start Celery worker in background
echo "Starting Celery worker..."
celery -A app.tasks.celery_app worker --loglevel=info --detach

# Start Celery beat in background
echo "Starting Celery beat..."
celery -A app.tasks.celery_app beat --loglevel=info --detach

# Start FastAPI
echo "Starting FastAPI..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
