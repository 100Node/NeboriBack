# Notifications Service

This service handles user notifications in the Nebori ecosystem. It listens for events on RabbitMQ and creates notifications for users.

## Features

- **Automatic Notifications**: Listens for `user_registered` events and creates a welcome notification.
- **REST API**: Allows frontend to fetch notifications for the logged-in user.
- **Read Status**: Mark individual or all notifications as read.

## API Documentation

### Base URL
`http://localhost:8005/api/notifications/` (Production)
`http://localhost:8106/api/notifications/` (Development)

### Authentication
All endpoints require a valid JWT token in the `Authorization` header:
`Authorization: Bearer <your_token>`

### Endpoints

#### 1. List Notifications
`GET /api/notifications/`
Returns a list of notifications for the current user.

**Response:**
```json
[
  {
    "id": 1,
    "user_id": 123,
    "message": "Welcome username! Your account has been successfully created.",
    "is_read": false,
    "created_at": "2026-05-09T00:00:00Z"
  }
]
```

#### 2. Mark Notification as Read
`POST /api/notifications/{id}/mark_as_read/`
Marks a specific notification as read.

**Response:**
```json
{
  "status": "notification marked as read"
}
```

#### 3. Mark All as Read
`POST /api/notifications/mark_all_as_read/`
Marks all unread notifications for the current user as read.

**Response:**
```json
{
  "status": "all notifications marked as read"
}
```

## Running the Service

### Prerequisites
- Docker and Docker Compose
- RabbitMQ (part of the infrastructure)
- PostgreSQL (part of the infrastructure)

### Setup
The service is automatically started when running `docker-compose up`.

To run the consumer manually:
```bash
python manage.py run_consumer
```
