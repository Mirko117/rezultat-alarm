#!/bin/sh
set -e

echo "Collecting static files..."
uv run manage.py collectstatic --noinput

echo "Running migrations..."
uv run manage.py migrate --noinput

echo "Starting application..."
exec "$@" # command from docker-compose.yml
