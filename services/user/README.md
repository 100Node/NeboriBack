# User Service API

The User Service handles user profiles, settings, and channel management with follower functionality.

## Base URL

```
http://localhost:8003/api/user/
```

## Endpoints

### User Profile

#### Get Current User Profile

```
GET /api/user/profile/me/
```

Returns the authenticated user's profile.

**Response:**

```json
{
  "id": 1,
  "username": "johndoe",
  "email": "john@example.com",
  "avatar": "http://localhost:8003/media/avatars/avatar.jpg",
  "bio": "My bio",
  "location": "New York",
  "website": "https://example.com",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

#### Update User Profile

```
PUT/PATCH /api/user/profile/update_profile/
```

Update user profile information (bio, location, website, avatar).

**Request Body:**

```json
{
  "bio": "Updated bio",
  "location": "Boston",
  "website": "https://newsite.com",
  "avatar": "<image_file>"
}
```

#### Change Avatar

```
PUT /api/user/profile/change_avatar/
```

Upload a new avatar image.

**Request (multipart/form-data):**

```
avatar: <image_file>
```

#### Get/Update User Settings

```
GET /api/user/profile/settings/
PUT/PATCH /api/user/profile/settings/
```

Get or update basic user settings (email, first_name, last_name).

**Request Body (for PUT/PATCH):**

```json
{
  "email": "newemail@example.com",
  "first_name": "John",
  "last_name": "Doe"
}
```

---

### Channels

#### List All Channels

```
GET /api/user/channels/
```

Returns a list of all channels with follower information.

#### Get Channel Details

```
GET /api/user/channels/{id}/
```

Returns detailed information about a specific channel.

#### Create a Channel

```
POST /api/user/channels/
```

Create a new channel.

**Request Body:**

```json
{
  "name": "My Channel",
  "description": "Channel description",
  "avatar": "<image_file>"
}
```

**Response:**

```json
{
  "id": 1,
  "name": "My Channel",
  "description": "Channel description",
  "avatar": "http://localhost:8003/media/channel_avatars/avatar.jpg",
  "owner_username": "johndoe",
  "followers_count": 0,
  "is_following": false,
  "followers": [],
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

#### Delete a Channel

```
DELETE /api/user/channels/{id}/
```

Delete a channel (only the owner can delete).

#### Follow a Channel

```
POST /api/user/channels/{id}/follow/
```

Follow a channel.

**Response:**

```json
{
  "message": "Followed My Channel"
}
```

#### Unfollow a Channel

```
DELETE /api/user/channels/{id}/follow/
```

Unfollow a channel.

#### Get Channel Followers

```
GET /api/user/channels/{id}/followers/
```

Returns list of followers for a specific channel.

**Response:**

```json
{
  "count": 5,
  "followers": [
    {
      "id": 1,
      "user_id": 2,
      "username": "user1",
      "followed_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

#### Get My Channels

```
GET /api/user/channels/my_channels/
```

Returns channels owned by the authenticated user.

#### Get Followed Channels

```
GET /api/user/channels/followed_channels/
```

Returns channels followed by the authenticated user.

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
- `204` - No Content
- `400` - Bad Request
- `403` - Forbidden
- `404` - Not Found
- `500` - Internal Server Error
