#!/usr/bin/env bash
set -e

# Run migrations & seeds only when starting uvicorn
case "$1" in
  uvicorn)
    echo "Running migrations..."
    # Don't exit if alembic fails (e.g. no versions yet)
    alembic upgrade head || echo "Alembic upgrade failed or no migrations found."
    ;;

  *)
esac

echo "Starting application..."
exec "$@"
