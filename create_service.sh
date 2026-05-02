#!/bin/bash

if [ -z "$1" ]; then
    echo "Error: Service name is required."
    echo "Usage: ./create_service.sh <service_name>"
    exit 1
fi

SERVICE_NAME=$1
echo "Generating structure for: $SERVICE_NAME..."

# Directories
mkdir -p "$SERVICE_NAME/app/core"
mkdir -p "$SERVICE_NAME/app/common"
mkdir -p "$SERVICE_NAME/app/modules/example_module"
mkdir -p "$SERVICE_NAME/alembic"

# Core and Common Files
touch "$SERVICE_NAME/app/core/__init__.py"
touch "$SERVICE_NAME/app/core/config.py"
touch "$SERVICE_NAME/app/core/database.py"
touch "$SERVICE_NAME/app/core/security.py"
touch "$SERVICE_NAME/app/core/exceptions.py"

touch "$SERVICE_NAME/app/common/__init__.py"
touch "$SERVICE_NAME/app/common/dependencies.py"

# Module Files
touch "$SERVICE_NAME/app/modules/__init__.py"
touch "$SERVICE_NAME/app/modules/example_module/__init__.py"
touch "$SERVICE_NAME/app/modules/example_module/router.py"
touch "$SERVICE_NAME/app/modules/example_module/schemas.py"
touch "$SERVICE_NAME/app/modules/example_module/models.py"
touch "$SERVICE_NAME/app/modules/example_module/service.py"

# Root Files
touch "$SERVICE_NAME/app/__init__.py"
touch "$SERVICE_NAME/alembic.ini"
touch "$SERVICE_NAME/Dockerfile"
touch "$SERVICE_NAME/.env"

# main.py template
cat <<EOF > "$SERVICE_NAME/app/main.py"
from fastapi import FastAPI

app = FastAPI(title="$SERVICE_NAME API", version="0.1.0")

@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "ok",
        "service": "$SERVICE_NAME"
    }
EOF

# requirements.txt template
cat <<EOF > "$SERVICE_NAME/requirements.txt"
fastapi
uvicorn[standard]
pydantic
pydantic-settings
sqlalchemy
alembic
asyncpg
EOF

# .gitignore template
cat <<EOF > "$SERVICE_NAME/.gitignore"
__pycache__/
*.pyc
.env
venv/
.venv/
alembic/versions/*.py
EOF

# .dockerignore template
cat <<EOF > "$SERVICE_NAME/.dockerignore"
.venv
venv
env
__pycache__
.Python
*.pyc
*.pyo
*.pyd
.git
.gitignore
.env
.env.*
.idea
.vscode
Dockerfile
EOF

echo "Done. Service $SERVICE_NAME created."