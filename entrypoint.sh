#!/bin/sh

echo "Waiting for DB..."
sleep 3

echo "Running migrations..."
alembic upgrade head

echo "Starting app..."
uvicorn app:create_app --factory --host 0.0.0.0 --port 8000