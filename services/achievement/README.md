# Achievement Service API

The Achievement Service tracks user points, achievements, and video watches.

## Base URL

```
http://localhost:8004/api/achievement/
```

## Endpoints

### Achievements

#### List All Achievements

```
GET /api/achievement/achievements/
```

Get all available achievements in the system.

**Response:**

```json
[
  {
    "id": 1,
    "name": "First Video",
    "description": "Watch your first video",
    "icon": "🎬",
    "achievement_type": "video_watch",
    "points_reward": 50,
    "requirement": 1
  }
]
```

#### Get Video Achievements

```
GET /api/achievement/achievements/video_achievements/
```

Get all video-related achievements.

---

### Points & Statistics

#### Get My Points

```
GET /api/achievement/points/my_points/
```

Get your current points summary.

**Response:**

```json
{
  "id": 1,
  "username": "johndoe",
  "total_points": 250,
  "points_from_videos": 250,
  "videos_watched": 25,
  "updated_at": "2024-01-01T00:00:00Z"
}
```

#### Get My Statistics

```
GET /api/achievement/points/my_stats/
```

Get comprehensive user statistics including rank.

**Response:**

```json
{
  "user_id": 1,
  "username": "johndoe",
  "total_points": 250,
  "points_from_videos": 250,
  "videos_watched": 25,
  "achievements_count": 5,
  "rank": 15
}
```

#### Get Leaderboard

```
GET /api/achievement/points/leaderboard/?limit=100
```

Get global leaderboard of top users.

**Response:**

```json
[
  {
    "rank": 1,
    "username": "top_user",
    "total_points": 5000,
    "videos_watched": 500,
    "achievements_count": 20
  },
  {
    "rank": 2,
    "username": "johndoe",
    "total_points": 250,
    "videos_watched": 25,
    "achievements_count": 5
  }
]
```

#### Get My Achievements

```
GET /api/achievement/points/user_achievements/
```

Get all achievements earned by the user.

**Response:**

```json
[
  {
    "id": 1,
    "achievement": {
      "id": 1,
      "name": "First Video",
      "description": "Watch your first video",
      "icon": "🎬",
      "achievement_type": "video_watch",
      "points_reward": 50,
      "requirement": 1
    },
    "earned_at": "2024-01-01T00:00:00Z"
  }
]
```

---

### Video Watches

#### Record Video Watch

```
POST /api/achievement/videos/record_watch/
```

Record that a user watched a video and award points.

**Request Body:**

```json
{
  "video_id": "video_123",
  "watch_duration": 600
}
```

**Response (First Watch):**

```json
{
  "message": "Video watched! +10 points",
  "watch": {
    "id": 1,
    "video_id": "video_123",
    "points_earned": 10,
    "watched_at": "2024-01-01T00:00:00Z",
    "watch_duration": 600
  },
  "total_points": 250
}
```

**Response (Already Watched):**

```json
{
  "message": "Video already watched",
  "points_earned": 0
}
```

#### Get My Watch History

```
GET /api/achievement/videos/my_watches/
```

Get user's video watch history.

**Response:**

```json
[
  {
    "id": 1,
    "video_id": "video_123",
    "points_earned": 10,
    "watched_at": "2024-01-01T00:00:00Z",
    "watch_duration": 600
  }
]
```

---

## Features

### Points System

- Users earn points for watching videos (default: 10 points per video)
- Each video can only be watched once for points
- Achievement bonuses are awarded on top of video points

### Achievement System

- **Video Watch Achievements**: Awarded when user watches a certain number of videos
  - 1 video watched: "First Video" (+50 points)
  - 10 videos watched: "Video Explorer" (+100 points)
  - 50 videos watched: "Video Master" (+250 points)

- **Points Milestone Achievements**: Awarded when user reaches certain points
  - 100 points: "Starter" (+50 points)
  - 500 points: "Enthusiast" (+100 points)
  - 1000 points: "Legend" (+200 points)

### Leaderboard

- Global ranking based on total points
- Top users are shown with their statistics
- Customizable limit parameter (default: 100)

---

## Authentication

All endpoints require JWT token authentication in the header:

```
Authorization: Bearer <your_jwt_token>
```

## Error Responses

```json
{
  "error": "Error message"
}
```

## Status Codes

- `200` - OK
- `201` - Created
- `400` - Bad Request
- `403` - Forbidden
- `404` - Not Found
- `500` - Internal Server Error
