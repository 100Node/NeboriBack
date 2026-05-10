#!/usr/bin/env bash
set -e

# Run migrations & seeds only when starting uvicorn
case "$1" in
  uvicorn)
    echo "Running migrations..."
    alembic upgrade head
    ;;

  *)
esac

echo "Starting application..."
exec "$@"