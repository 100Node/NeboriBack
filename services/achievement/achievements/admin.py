from django.contrib import admin
from .models import Achievement, UserPoints, UserAchievement, VideoWatch


@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ["name", "achievement_type", "points_reward", "requirement"]
    search_fields = ["name", "description"]
    list_filter = ["achievement_type", "created_at"]


@admin.register(UserPoints)
class UserPointsAdmin(admin.ModelAdmin):
    list_display = ["user", "total_points", "videos_watched", "updated_at"]
    search_fields = ["user__username"]
    readonly_fields = ["updated_at"]
    list_filter = ["updated_at"]


@admin.register(UserAchievement)
class UserAchievementAdmin(admin.ModelAdmin):
    list_display = ["user", "achievement", "earned_at"]
    search_fields = ["user__username", "achievement__name"]
    readonly_fields = ["earned_at"]
    list_filter = ["earned_at"]


@admin.register(VideoWatch)
class VideoWatchAdmin(admin.ModelAdmin):
    list_display = ["user", "video_id", "points_earned", "watched_at"]
    search_fields = ["user__username", "video_id"]
    readonly_fields = ["watched_at"]
    list_filter = ["watched_at"]
