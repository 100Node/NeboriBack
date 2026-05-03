from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    avatar = models.ImageField(upload_to="avatars/", null=True, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=100, blank=True)
    website = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} Profile"


class Channel(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="owned_channels")
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    avatar = models.ImageField(upload_to="channel_avatars/", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name


class ChannelFollower(models.Model):
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE, related_name="followers")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="following_channels")
    followed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("channel", "user")
        ordering = ["-followed_at"]

    def __str__(self):
        return f"{self.user.username} follows {self.channel.name}"
