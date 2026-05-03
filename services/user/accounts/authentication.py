from django.contrib.auth import get_user_model
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed


class AutoCreateJWTAuthentication(JWTAuthentication):
    """Wrapper around SimpleJWT's JWTAuthentication that auto-creates
    a local User record if a token is valid but the user does not exist.

    This addresses cross-service tokens issued by an auth service where
    the user record may not yet exist in this service's database.
    """

    def get_user(self, validated_token):
        User = get_user_model()
        try:
            return super().get_user(validated_token)
        except AuthenticationFailed:
            # Try to recover by creating the user referenced in the token.
            user_id = validated_token.get("user_id") or validated_token.get("user")
            if not user_id:
                raise
            # Create a minimal user with the provided id. Username must be unique,
            # so use a generated value if none is available.
            defaults = {"username": f"user_{user_id}"}
            user, created = User.objects.get_or_create(id=user_id, defaults=defaults)
            return user
