#!/bin/sh
set -e

echo "Waiting for PostgreSQL..."
while ! pg_isready -h db -p 5432 -U postgres; do
    sleep 1
done
echo "PostgreSQL is ready!"

echo "Running database migrations..."
cd /app
alembic upgrade head
echo "Migrations complete!"

echo "Starting application..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
