from enum import StrEnum


class VideoStatusEnum(StrEnum):
    QUEUED = "queued"          # запис створено, очікує завантаження
    UPLOADING = "uploading"    # файл завантажується в S3
    TRANSCODING = "transcoding"  # транскодинг в процесі
    PUBLISHED = "published"    # готово, доступно для перегляду
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