# Video Metadata Service API

The Video Metadata Service manages video metadata, including CRUD operations and status management.

## Base URL

```
http://localhost:<port>/api/v1/
```

## Endpoints

### Videos

#### Create Video Metadata

```
POST /api/v1/videos/
```

Create new video metadata entry.

**Request Body:**

```json
{
  "title": "My Video",
  "description": "Video description",
  "user_id": "uuid-string"
}
```

**Response:**

```json
{
  "id": "uuid",
  "user_id": "uuid",
  "title": "My Video",
  "description": "Video description",
  "status": "pending",
  "playlist_url": null,
  "thumbnail_url": null,
  "duration": null,
  "views_count": 0,
  "created_at": "2024-01-01T00:00:00Z"
}
```

---

#### Get Video Metadata

```
GET /api/v1/videos/{video_id}
```

Get metadata for a specific video.

**Response:**

```json
{
  "id": "uuid",
  "user_id": "uuid",
  "title": "My Video",
  "description": "Video description",
  "status": "processed",
  "playlist_url": "path/to/playlist.m3u8",
  "thumbnail_url": "path/to/thumbnail.jpg",
  "duration": 300,
  "views_count": 42,
  "created_at": "2024-01-01T00:00:00Z"
}
```

---

#### List Videos

```
GET /api/v1/videos/
```

List videos with pagination.

**Query Parameters:**
- `limit` (int, default 20): Number of items to return
- `offset` (int, default 0): Offset for pagination

**Response:**

```json
[
  {
    "id": "uuid",
    "user_id": "uuid",
    "title": "My Video",
    "description": "Video description",
    "status": "processed",
    "playlist_url": "path/to/playlist.m3u8",
    "thumbnail_url": "path/to/thumbnail.jpg",
    "duration": 300,
    "views_count": 42,
    "created_at": "2024-01-01T00:00:00Z"
  }
]
```

---

#### Update Video Metadata

```
PATCH /api/v1/videos/{video_id}
```

Update video metadata.

**Request Body:**

```json
{
  "title": "Updated Title",
  "description": "Updated description",
  "status": "processed"
}
```

**Response:**

```json
{
  "id": "uuid",
  "user_id": "uuid",
  "title": "Updated Title",
  "description": "Updated description",
  "status": "processed",
  "playlist_url": "path/to/playlist.m3u8",
  "thumbnail_url": "path/to/thumbnail.jpg",
  "duration": 300,
  "views_count": 42,
  "created_at": "2024-01-01T00:00:00Z"
}
```

---

#### Delete Video

```
DELETE /api/v1/videos/{video_id}
```

Delete a video.

**Response:** No content (204)

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
- `204` - No Content
- `404` - Not Found
- `500` - Internal Server Error
