from jose import JWTError, jwt
from passlib.context import CryptContext
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def decode_token(token: str) -> dict:
    return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])


# Reset password token

def verify_reset_token_signature(token: str, password_hash: str) -> bool:
    """
    Verifies if reset password token signature is valid 
    """
    dynamic_secret = f"{settings.JWT_SECRET_KEY}{password_hash}"
    try:
        jwt.decode(token, dynamic_secret, algorithms=[settings.JWT_ALGORITHM])
        return True
    except JWTError:
        return False