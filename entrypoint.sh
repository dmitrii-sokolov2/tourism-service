#!/bin/sh

echo "Waiting for DB..."
sleep 3

echo "Running migrations..."
flask db upgrade

echo "Starting app..."
gunicorn "app:create_app()" -w 4 -b 0.0.0.0:5000