from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import HealthAPIView, LoginAPIView, ProfileAPIView, RegisterAPIView

urlpatterns = [
    path("health/", HealthAPIView.as_view(), name="health"),
    path("register/", RegisterAPIView.as_view(), name="register"),
    path("login/", LoginAPIView.as_view(), name="login"),
    path("refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("me/", ProfileAPIView.as_view(), name="profile"),
]
