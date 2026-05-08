from enum import StrEnum


class VideoStatusEnum(StrEnum):
    UPLOADING = "uploading"
    PROCESSING = "processing"
    PUBLISHED = "published"
    BLOCKED = "blocked"
    DELETED = "deleted"
    ERROR = "error"
    CANCELED = "canceled"


class CommentStatus(StrEnum):
    ACTIVE = "active"
    DELETED = "deleted"


class ReactionType(StrEnum):
    LIKE = "like"
    DISLIKE = "dislike"
