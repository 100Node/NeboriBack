from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AchievementViewSet, UserPointsViewSet, VideoWatchViewSet

router = DefaultRouter()
router.register(r"achievements", AchievementViewSet, basename="achievement")
router.register(r"points", UserPointsViewSet, basename="points")
router.register(r"videos", VideoWatchViewSet, basename="video")

urlpatterns = [
    path("", include(router.urls)),
]
