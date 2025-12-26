#!/bin/bash

# Database migration script
# Usage: ./run-migrations.sh [dev|test]

set -e

ENV=${1:-dev}

if [ "$ENV" = "test" ]; then
    DB_HOST=${TEST_DB_HOST:-localhost}
    DB_PORT=${TEST_DB_PORT:-5433}
    DB_NAME=${TEST_DB_NAME:-news_test_db}
    DB_USER=${TEST_DB_USER:-news_user}
    DB_PASSWORD=${TEST_DB_PASSWORD:-news_password}
else
    DB_HOST=${DB_HOST:-localhost}
    DB_PORT=${DB_PORT:-5432}
    DB_NAME=${DB_NAME:-news_db}
    DB_USER=${DB_USER:-news_user}
    DB_PASSWORD=${DB_PASSWORD:-news_password}
fi

echo "Running migrations for $ENV environment..."
echo "Database: $DB_NAME on $DB_HOST:$DB_PORT"

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
MIGRATIONS_DIR="$SCRIPT_DIR/migrations"

export PGPASSWORD=$DB_PASSWORD

# Run each migration file in order
for file in "$MIGRATIONS_DIR"/*.sql; do
    if [ -f "$file" ]; then
        echo "Running migration: $(basename $file)"
        psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" < "$file"
    fi
done

echo "Migrations completed successfully!"
