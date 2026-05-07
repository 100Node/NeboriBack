#!/bin/sh
set -e

echo "Creating additional databases..."

for db in nebori_auth nebori_user auth_db video_metadata_db upload_tasks_db transcoding_db achievements_db; do
    echo "Checking $db..."
    if ! psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "postgres" -tAc "SELECT 1 FROM pg_database WHERE datname='$db'" | grep -q 1; then
        echo "Creating database $db..."
        psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "postgres" <<-EOSQL
            CREATE DATABASE $db;
            GRANT ALL PRIVILEGES ON DATABASE $db TO $POSTGRES_USER;
EOSQL
    else
        echo "Database $db already exists!"
    fi
done
