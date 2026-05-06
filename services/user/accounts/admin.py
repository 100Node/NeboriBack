from django.contrib import admin
from .models import UserProfile, Channel, ChannelFollower


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "created_at", "updated_at"]
    search_fields = ["user__username", "bio"]
    readonly_fields = ["created_at", "updated_at"]


@admin.register(Channel)
class ChannelAdmin(admin.ModelAdmin):
    list_display = ["name", "owner", "created_at"]
    search_fields = ["name", "owner__username"]
    readonly_fields = ["created_at", "updated_at"]
    list_filter = ["created_at"]


@admin.register(ChannelFollower)
class ChannelFollowerAdmin(admin.ModelAdmin):
    list_display = ["user", "channel", "followed_at"]
    search_fields = ["user__username", "channel__name"]
    readonly_fields = ["followed_at"]
    list_filter = ["followed_at"]
