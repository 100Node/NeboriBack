from django.db import models
from django.contrib.auth.models import User


class Achievement(models.Model):
    """Achievement definition - represents different achievement types"""
    ACHIEVEMENT_TYPES = [
        ("video_watch", "Video Watch"),
        ("video_milestone", "Video Watch Milestone"),
        ("points_milestone", "Points Milestone"),
    ]

    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    icon = models.CharField(max_length=50, default="star")  # emoji or icon name
    achievement_type = models.CharField(max_length=20, choices=ACHIEVEMENT_TYPES)
    points_reward = models.IntegerField(default=0)
    requirement = models.IntegerField(default=1)  # e.g., watch 10 videos, earn 100 points
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class UserPoints(models.Model):
    """Track total points for each user"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="points")
    total_points = models.IntegerField(default=0)
    points_from_videos = models.IntegerField(default=0)
    videos_watched = models.IntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-total_points"]

    def __str__(self):
        return f"{self.user.username} - {self.total_points} points"


class UserAchievement(models.Model):
    """Track achievements earned by users"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="achievements")
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE)
    earned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "achievement")
        ordering = ["-earned_at"]

    def __str__(self):
        return f"{self.user.username} - {self.achievement.name}"


class VideoWatch(models.Model):
    """Track video watch events"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="video_watches")
    video_id = models.CharField(max_length=255)  # external video ID
    points_earned = models.IntegerField(default=10)
    watched_at = models.DateTimeField(auto_now_add=True)
    watch_duration = models.IntegerField(null=True, blank=True)  # in seconds

    class Meta:
        ordering = ["-watched_at"]
        unique_together = ("user", "video_id")  # prevent duplicate watches for same video

    def __str__(self):
        return f"{self.user.username} watched video {self.video_id}"
