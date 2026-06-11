set -e

echo "Running migration......."
alembic upgrade head

echo "starting server........."
uvicorn main:app --host 0.0.0.0 --port 8000