from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth.models import User
from django.db.models import Count, F
from .models import Achievement, UserPoints, UserAchievement, VideoWatch
from .serializers import (
    AchievementSerializer,
    UserPointsSerializer,
    UserAchievementSerializer,
    VideoWatchSerializer,
    UserStatsSerializer,
    LeaderboardSerializer,
)


class AchievementViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Achievement.objects.all()
    serializer_class = AchievementSerializer
    permission_classes = [AllowAny]

    @action(detail=False, methods=["get"])
    def video_achievements(self, request):
        """Get all video-related achievements"""
        achievements = Achievement.objects.filter(achievement_type="video_watch")
        serializer = AchievementSerializer(achievements, many=True)
        return Response(serializer.data)


class UserPointsViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=["get"])
    def my_points(self, request):
        """Get current user's points"""
        user_points, created = UserPoints.objects.get_or_create(user=request.user)
        serializer = UserPointsSerializer(user_points)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def my_stats(self, request):
        """Get comprehensive user statistics"""
        user_points, created = UserPoints.objects.get_or_create(user=request.user)
        achievements_count = UserAchievement.objects.filter(user=request.user).count()

        # Calculate rank
        rank = (
            UserPoints.objects.filter(total_points__gt=user_points.total_points).count() + 1
        )

        stats = {
            "user_id": request.user.id,
            "username": request.user.username,
            "total_points": user_points.total_points,
            "points_from_videos": user_points.points_from_videos,
            "videos_watched": user_points.videos_watched,
            "achievements_count": achievements_count,
            "rank": rank,
        }
        serializer = UserStatsSerializer(stats)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def leaderboard(self, request):
        """Get global leaderboard"""
        limit = int(request.query_params.get("limit", 100))
        leaderboard = (
            UserPoints.objects.select_related("user")
            .annotate(
                achievements_count=Count("user__achievements"),
            )
            .order_by("-total_points")[:limit]
        )

        data = []
        for rank, entry in enumerate(leaderboard, 1):
            data.append(
                {
                    "rank": rank,
                    "username": entry.user.username,
                    "total_points": entry.total_points,
                    "videos_watched": entry.videos_watched,
                    "achievements_count": entry.achievements_count,
                }
            )

        serializer = LeaderboardSerializer(data, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def user_achievements(self, request):
        """Get all user achievements"""
        user_achievements = UserAchievement.objects.filter(user=request.user).select_related(
            "achievement"
        )
        serializer = UserAchievementSerializer(user_achievements, many=True)
        return Response(serializer.data)


class VideoWatchViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=["post"])
    def record_watch(self, request):
        """Record a video watch and award points"""
        video_id = request.data.get("video_id")
        watch_duration = request.data.get("watch_duration", None)

        if not video_id:
            return Response(
                {"error": "video_id is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Check if video was already watched
        video_watch, created = VideoWatch.objects.get_or_create(
            user=request.user, video_id=video_id, defaults={"watch_duration": watch_duration}
        )

        if not created:
            return Response(
                {"message": "Video already watched", "points_earned": 0},
                status=status.HTTP_200_OK,
            )

        # Update user points
        user_points, _ = UserPoints.objects.get_or_create(user=request.user)
        points_to_add = video_watch.points_earned

        user_points.total_points += points_to_add
        user_points.points_from_videos += points_to_add
        user_points.videos_watched += 1
        user_points.save()

        # Check for achievements
        self._check_achievements(request.user, user_points)

        serializer = VideoWatchSerializer(video_watch)
        return Response(
            {
                "message": f"Video watched! +{points_to_add} points",
                "watch": serializer.data,
                "total_points": user_points.total_points,
            },
            status=status.HTTP_201_CREATED,
        )

    @action(detail=False, methods=["get"])
    def my_watches(self, request):
        """Get user's video watch history"""
        watches = VideoWatch.objects.filter(user=request.user).order_by("-watched_at")
        serializer = VideoWatchSerializer(watches, many=True)
        return Response(serializer.data)

    def _check_achievements(self, user, user_points):
        """Check and award achievements based on user's progress"""
        achievements = Achievement.objects.all()

        for achievement in achievements:
            # Skip if already earned
            if UserAchievement.objects.filter(user=user, achievement=achievement).exists():
                continue

            # Check video milestone achievements
            if achievement.achievement_type == "video_watch":
                if user_points.videos_watched >= achievement.requirement:
                    UserAchievement.objects.create(user=user, achievement=achievement)
                    user_points.total_points += achievement.points_reward
                    user_points.save()

            # Check points milestone achievements
            elif achievement.achievement_type == "points_milestone":
                if user_points.total_points >= achievement.requirement:
                    UserAchievement.objects.create(user=user, achievement=achievement)
                    user_points.total_points += achievement.points_reward
                    user_points.save()
