# Upload Service API

The Upload Service handles video file uploads to storage and initiates processing.

## Base URL

```
http://localhost:8000/api/v1/
```

## Endpoints

### Videos

#### Upload Video

```
POST /api/v1/videos/
```

Upload a video file and create an upload record.

**Request (multipart/form-data):**

```
title: "My Video Title"
video_id: "uuid-string"
user_id: "uuid-string"
file: <video_file>
```

**Response:**

```json
{
  "id": "uuid",
  "video_id": "uuid",
  "user_id": "uuid",
  "title": "My Video Title",
  "filename": "video.mp4",
  "s3_path": "path/to/video.mp4",
  "status": "uploaded",
  "created_at": "2024-01-01T00:00:00Z"
}
```

---

## Health Check

```
GET /health
```

Returns service health status.

**Response:**

```json
{
  "status": "ok",
  "service": "upload_video"
}
```

---

## Error Responses

```json
{
  "detail": "Error message"
}
```

---

## Status Codes

- `200` - OK
- `201` - Created
- `400` - Bad Request
- `500` - Internal Server Error
