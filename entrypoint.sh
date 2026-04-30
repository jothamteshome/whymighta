#!/bin/bash
set -e

if [ "$ENV" = "production" ]; then
    echo "Creating database if not exists..."
    PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USERNAME" -d postgres \
    -c "CREATE DATABASE \"$DB_DATABASE\";" || true
fi

exec python main.py