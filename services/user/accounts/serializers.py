from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile, Channel, ChannelFollower


class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    email = serializers.CharField(source="user.email", read_only=True)

    class Meta:
        model = UserProfile
        fields = ["id", "username", "email", "avatar", "bio", "location", "website", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class UserSettingsSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name", "profile"]
        read_only_fields = ["id", "username"]


class ChannelFollowerSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    user_id = serializers.IntegerField(source="user.id", read_only=True)

    class Meta:
        model = ChannelFollower
        fields = ["id", "user_id", "username", "followed_at"]
        read_only_fields = ["id", "followed_at"]


class ChannelSerializer(serializers.ModelSerializer):
    owner_username = serializers.CharField(source="owner.username", read_only=True)
    followers_count = serializers.SerializerMethodField()
    is_following = serializers.SerializerMethodField()
    followers = ChannelFollowerSerializer(many=True, read_only=True)

    class Meta:
        model = Channel
        fields = [
            "id",
            "name",
            "description",
            "avatar",
            "owner_username",
            "followers_count",
            "is_following",
            "followers",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "owner_username", "created_at", "updated_at"]

    def get_followers_count(self, obj):
        return obj.followers.count()

    def get_is_following(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return obj.followers.filter(user=request.user).exists()
        return False


class ChannelCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Channel
        fields = ["name", "description", "avatar"]
