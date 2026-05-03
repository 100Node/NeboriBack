from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Achievement, UserPoints, UserAchievement, VideoWatch


class AchievementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Achievement
        fields = ["id", "name", "description", "icon", "achievement_type", "points_reward", "requirement"]
        read_only_fields = ["id"]


class UserAchievementSerializer(serializers.ModelSerializer):
    achievement = AchievementSerializer(read_only=True)

    class Meta:
        model = UserAchievement
        fields = ["id", "achievement", "earned_at"]
        read_only_fields = ["id", "earned_at"]


class VideoWatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = VideoWatch
        fields = ["id", "video_id", "points_earned", "watched_at", "watch_duration"]
        read_only_fields = ["id", "watched_at"]


class UserPointsSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = UserPoints
        fields = [
            "id",
            "username",
            "total_points",
            "points_from_videos",
            "videos_watched",
            "updated_at",
        ]
        read_only_fields = ["id", "updated_at"]


class UserStatsSerializer(serializers.Serializer):
    """Comprehensive user statistics"""
    user_id = serializers.IntegerField()
    username = serializers.CharField()
    total_points = serializers.IntegerField()
    points_from_videos = serializers.IntegerField()
    videos_watched = serializers.IntegerField()
    achievements_count = serializers.IntegerField()
    rank = serializers.IntegerField()


class LeaderboardSerializer(serializers.Serializer):
    """Leaderboard entry"""
    rank = serializers.IntegerField()
    username = serializers.CharField()
    total_points = serializers.IntegerField()
    videos_watched = serializers.IntegerField()
    achievements_count = serializers.IntegerField()
