#!/bin/bash
set -e

if [ "$ENV" = "production" ]; then
    echo "Creating database if not exists..."
    psql "postgresql://$DB_USERNAME:$DB_PASSWORD@$DB_HOST:$DB_PORT/postgres" \
        -c "CREATE DATABASE \"$DB_DATABASE\";" 2>/dev/null || true
fi

exec python main.py