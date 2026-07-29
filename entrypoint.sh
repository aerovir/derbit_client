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

# Graceful shutdown handler
_shutdown() {
    echo "Shutting down..."
    kill -TERM "$CELERY_BEAT_PID" 2>/dev/null || true
    kill -TERM "$CELERY_WORKER_PID" 2>/dev/null || true
    kill -TERM "$UVICORN_PID" 2>/dev/null || true
    wait "$CELERY_BEAT_PID" 2>/dev/null || true
    wait "$CELERY_WORKER_PID" 2>/dev/null || true
    wait "$UVICORN_PID" 2>/dev/null || true
    echo "Shutdown complete."
    exit 0
}

trap _shutdown SIGTERM SIGINT

# Start Celery worker in background
echo "Starting Celery worker..."
celery -A app.tasks.celery_app worker --loglevel=info &
CELERY_WORKER_PID=$!

# Start Celery beat in background
echo "Starting Celery beat..."
celery -A app.tasks.celery_app beat --loglevel=info &
CELERY_BEAT_PID=$!

# Start FastAPI
echo "Starting FastAPI..."
uvicorn app.main:app --host 0.0.0.0 --port 8000 &
UVICORN_PID=$!

# Wait for any process to exit
wait -n
# If we get here, one process exited unexpectedly — shut down the rest
_shutdown
