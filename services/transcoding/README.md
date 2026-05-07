# Transcoding Service

The Transcoding Service handles video transcoding to HLS format and processes videos via RabbitMQ events.

## Overview

This service doesn't expose HTTP endpoints. Instead, it listens to RabbitMQ events for:
- Video upload completion to start processing
- Video cancellation requests to stop processing

## Events

### Subscribed Events

#### 1. Video Upload Event

**Queue:** `video.upload.events`

**Payload:**

```json
{
  "payload": {
    "video_id": "uuid",
    "user_id": "uuid",
    "s3_bucket": "bucket-name",
    "s3_path": "path/to/video.mp4"
  }
}
```

**Processing:**
1. Downloads video from S3
2. Extracts audio
3. Transcodes to HLS (1080p and 720p)
4. Uploads processed files back to S3

---

#### 2. Video Cancel Event

**Queue:** `video.canceled.events`

**Payload:**

```json
{
  "payload": {
    "video_id": "uuid"
  }
}
```

**Action:** Cancels the active transcoding task for the specified video.

---

### Published Events

#### 1. Video Processed Event

**Queue:** `video.processing.done`

**Payload:**

```json
{
  "payload": {
    "video_id": "uuid",
    "audio_path": "path/to/audio.mp3",
    "video_1080p_path": "path/to/1080p/index.m3u8",
    "video_720p_path": "path/to/720p/index.m3u8"
  }
}
```

---

## Processing Pipeline

The service processes videos through these steps:
1. Download raw video from S3
2. Extract audio (MP3)
3. Transcode video to HLS at 1080p and 720p resolutions
4. Upload processed files back to S3
5. Publish success event

---

## Temporary Storage

Processed files are stored temporarily in `/tmp/nebori_processing` and cleaned up after completion.

---

## Error Handling

Errors during processing are logged and re-raised to be handled by the message broker.
