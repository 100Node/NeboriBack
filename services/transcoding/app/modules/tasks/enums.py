from enum import StrEnum

class TaskStatusEnum(StrEnum):
    PENDING = "pending"         # Чекає в черзі
    PROCESSING = "processing"   # FFmpeg працює прямо зараз
    COMPLETED = "completed"     # Успішно закінчено
    FAILED = "failed"           # FFmpeg впав (не вистачило пам'яті, битий файл)

class TaskTypeEnum(StrEnum):
    EXTRACT_AUDIO = "extract_audio"
    TRANSCODE_1080P = "transcode_1080p"
    TRANSCODE_720P = "transcode_720p"
    TRANSCODE_480P = "transcode_480p"