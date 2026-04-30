#!/bin/bash
set -e

if [ "$ENV" = "production" ]; then
    echo "Fetching environment variables from AWS SSM..."

    export DB_USERNAME=$(aws ssm get-parameter --name "/whymighta/db/username" --with-decryption --query "Parameter.Value" --output text)
    export DB_PASSWORD=$(aws ssm get-parameter --name "/whymighta/db/password" --with-decryption --query "Parameter.Value" --output text)
    export DB_HOST=$(aws ssm get-parameter --name "/whymighta/db/host" --with-decryption --query "Parameter.Value" --output text)
    export DB_PORT=$(aws ssm get-parameter --name "/whymighta/db/port" --with-decryption --query "Parameter.Value" --output text)
    export DB_DATABASE=$(aws ssm get-parameter --name "/whymighta/db/database" --with-decryption --query "Parameter.Value" --output text)
    echo "Database environment variables set!";

    export AWS_CHATGPT_API_URL=$(aws ssm get-parameter --name "/whymighta/api/chatgpt/url" --with-decryption --query "Parameter.Value" --output text)
    export AWS_CHATGPT_API_KEY=$(aws ssm get-parameter --name "/whymighta/api/chatgpt/key" --with-decryption --query "Parameter.Value" --output text)
    echo "ChatGPT API environment variables set!";

    export WEATHER_API_KEY=$(aws ssm get-parameter --name "/whymighta/api/weather/key" --with-decryption --query "Parameter.Value" --output text)
    export DISCORD_TOKEN=$(aws ssm get-parameter --name "/whymighta/discord/token" --with-decryption --query "Parameter.Value" --output text)
    echo "All environment variables set!"

    echo "Creating database if not exists..."
    psql "postgresql://$DB_USERNAME:$DB_PASSWORD@$DB_HOST:$DB_PORT/postgres" \
        -c "CREATE DATABASE \"$DB_DATABASE\";" 2>/dev/null || true
fi

exec python main.py