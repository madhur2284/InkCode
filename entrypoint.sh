#!/bin/bash
set -e

echo "Running migrations..."
alembic upgrade head

echo "Starting server..."
exec gunicorn main:app \
    -k uvicorn.workers.UvicornWorker \
    --workers 2 \
    --bind 0.0.0.0:$PORT \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -