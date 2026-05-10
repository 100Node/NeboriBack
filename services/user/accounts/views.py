from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth.models import User
from .models import UserProfile, Channel, ChannelFollower
from .serializers import (
    UserProfileSerializer,
    UserSettingsSerializer,
    ChannelSerializer,
    ChannelCreateSerializer,
    ChannelFollowerSerializer,
)


class UserProfileViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=["get"])
    def me(self, request):
        """Get current user profile"""
        try:
            profile = request.user.profile
        except UserProfile.DoesNotExist:
            profile = UserProfile.objects.create(user=request.user)
        
        serializer = UserProfileSerializer(profile, context={"request": request})
        return Response(serializer.data)

    @action(detail=False, methods=["put", "patch"])
    def update_profile(self, request):
        """Update user profile (avatar, bio, location, website)"""
        try:
            profile = request.user.profile
        except UserProfile.DoesNotExist:
            profile = UserProfile.objects.create(user=request.user)
        
        serializer = UserProfileSerializer(profile, data=request.data, partial=True, context={"request": request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["put"])
    def change_avatar(self, request):
        """Change user avatar"""
        try:
            profile = request.user.profile
        except UserProfile.DoesNotExist:
            profile = UserProfile.objects.create(user=request.user)
        
        if "avatar" not in request.FILES:
            return Response({"error": "Avatar file is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        profile.avatar = request.FILES["avatar"]
        profile.save()
        serializer = UserProfileSerializer(profile, context={"request": request})
        return Response(serializer.data)

    @action(detail=False, methods=["get", "put", "patch"], url_path="settings")
    def user_settings(self, request):
        """Get or update user settings"""
        # Ensure user has a profile
        try:
            profile = request.user.profile
        except UserProfile.DoesNotExist:
            profile = UserProfile.objects.create(user=request.user)
        
        if request.method == "GET":
            serializer = UserSettingsSerializer(request.user, context={"request": request})
            return Response(serializer.data)
        
        try:
            serializer = UserSettingsSerializer(
                request.user, 
                data=request.data, 
                partial=True, 
                context={"request": request}
            )
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ChannelViewSet(viewsets.ModelViewSet):
    queryset = Channel.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == "create":
            return ChannelCreateSerializer
        return ChannelSerializer

    def create(self, request, *args, **kwargs):
        """Create a new channel"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        channel = serializer.save(owner=request.user)
        serializer = ChannelSerializer(channel, context={"request": request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def list(self, request, *args, **kwargs):
        """List all channels"""
        queryset = self.get_queryset()
        serializer = ChannelSerializer(queryset, many=True, context={"request": request})
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        """Get channel details"""
        channel = self.get_object()
        serializer = ChannelSerializer(channel, context={"request": request})
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        """Delete a channel (only owner can delete)"""
        channel = self.get_object()
        if channel.owner != request.user:
            return Response({"error": "You can only delete your own channels"}, status=status.HTTP_403_FORBIDDEN)
        channel.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["post", "delete"])
    def follow(self, request, pk=None):
        """Follow or unfollow a channel"""
        channel = self.get_object()
        
        if request.method == "POST":
            # Follow channel
            follower, created = ChannelFollower.objects.get_or_create(channel=channel, user=request.user)
            if created:
                return Response({"message": f"Followed {channel.name}"}, status=status.HTTP_201_CREATED)
            return Response({"message": "Already following this channel"}, status=status.HTTP_200_OK)
        
        else:  # DELETE
            # Unfollow channel
            follower = ChannelFollower.objects.filter(channel=channel, user=request.user).first()
            if follower:
                follower.delete()
                return Response({"message": f"Unfollowed {channel.name}"}, status=status.HTTP_204_NO_CONTENT)
            return Response({"error": "Not following this channel"}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=["get"])
    def followers(self, request, pk=None):
        """Get all followers of a channel"""
        channel = self.get_object()
        followers = channel.followers.all()
        serializer = ChannelFollowerSerializer(followers, many=True, context={"request": request})
        return Response({"count": followers.count(), "followers": serializer.data})

    @action(detail=False, methods=["get"])
    def my_channels(self, request):
        """Get channels owned by the current user"""
        channels = Channel.objects.filter(owner=request.user)
        serializer = ChannelSerializer(channels, many=True, context={"request": request})
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def followed_channels(self, request):
        """Get channels followed by the current user"""
        followed_channels = Channel.objects.filter(followers__user=request.user)
        serializer = ChannelSerializer(followed_channels, many=True, context={"request": request})
        return Response(serializer.data)
