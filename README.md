# NeboriBack Microservices

This repository now includes a Django-based `auth` microservice and supporting Docker setup.

## Services

- `auth` (Django + DRF + JWT) on port `8002`
- `db` (PostgreSQL for auth service)
- `minio` (object storage) on ports `9000` and `9001`

## Run With Docker Compose

```bash
docker compose up --build
```

## Auth API

Base URL:

```text
http://localhost:8002/api/auth/
```

Endpoints:

- `GET health/` - service health check
- `POST register/` - create a new user and return JWT tokens
- `POST login/` - get access/refresh tokens (`username`, `password`)
- `POST refresh/` - refresh access token
- `GET me/` - get current user profile (requires `Authorization: Bearer <token>`)

### Example Request: Register

```bash
curl -X POST http://localhost:8002/api/auth/register/ \
	-H "Content-Type: application/json" \
	-d '{
		"username": "demo",
		"email": "demo@example.com",
		"password": "demoPass123",
		"password_confirm": "demoPass123"
	}'
```
