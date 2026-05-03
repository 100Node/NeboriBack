from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserProfileViewSet, ChannelViewSet

router = DefaultRouter()
router.register(r"profile", UserProfileViewSet, basename="profile")
router.register(r"channels", ChannelViewSet, basename="channel")

urlpatterns = [
    path("", include(router.urls)),
]
