#!/usr/bin/env bash
set -e

echo "Running database migrations..."
alembic upgrade head

echo "Seeding initial admin user..."
python -m src.seed

exec "$@"