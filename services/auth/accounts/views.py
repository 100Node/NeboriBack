from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from .serializers import RegisterResponseSerializer, RegisterSerializer, UserSerializer
from .rabbitmq import publish_message


class RegisterAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        payload = RegisterResponseSerializer.build_payload(user)
        
        try:
            publish_message(
                queue_name="user_registered",
                message={
                    "event": "user_registered",
                    "user_id": user.id,
                    "username": user.username,
                    "email": user.email
                }
            )
        except Exception as e:
            print(f"Failed to publish user_registered event: {e}")
            
        return Response(payload, status=status.HTTP_201_CREATED)


class ProfileAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        try:
            publish_message(
                queue_name="profile_accessed",
                message={
                    "event": "profile_accessed",
                    "user_id": request.user.id,
                    "username": request.user.username
                }
            )
        except Exception as e:
            print(f"Failed to publish profile_accessed event: {e}")
            
        return Response(UserSerializer(request.user).data)


class HealthAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        return Response({"status": "ok", "service": "auth"}, status=status.HTTP_200_OK)


class LoginAPIView(TokenObtainPairView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            user_id = None
            try:
                from rest_framework_simplejwt.tokens import AccessToken
                access_token = response.data.get("access")
                if access_token:
                    token = AccessToken(access_token)
                    user_id = token.get("user_id")
                    username = request.data.get("username")
                    
                    publish_message(
                        queue_name="user_logged_in",
                        message={
                            "event": "user_logged_in",
                            "user_id": user_id,
                            "username": username
                        }
                    )
            except Exception as e:
                print(f"Failed to publish user_logged_in event: {e}")
                
        return response
