#!/bin/sh
set -e

PGUSER="nebori"
PGPASSWORD="nebori"
PGHOST="db"
PGPORT="5432"

export PGUSER PGPASSWORD PGHOST PGPORT

echo "Checking if nebori_user database exists..."
if ! psql -d postgres -tAc "SELECT 1 FROM pg_database WHERE datname='nebori_user'" | grep -q 1; then
    echo "Creating nebori_user database..."
    createdb nebori_user
else
    echo "nebori_user database already exists!"
fi
