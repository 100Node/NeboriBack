from datetime import datetime
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError

from app.core.security import decode_token
from app.common.schemas import TokenData

bearer = HTTPBearer(auto_error=False)

async def get_token_data(
    creds: HTTPAuthorizationCredentials | None = Depends(bearer),
) -> TokenData:
    """
    Basic dependency.
    1. Checks the validity of the token.

    Used for general endpoints: registration, document upload, profile.
    """
    
    if creds is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="auth.missing_token"
        )

    try:
        payload = decode_token(creds.credentials)

        user_id = payload.get("user_id")
        exp = payload.get("exp")
        iat = payload.get("iat")
        jti = payload.get("jti")
        token_type = payload.get("token_type")

        if user_id is None or exp is None or iat is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="auth.invalid_token"
            )

        token = TokenData(
            exp=datetime.fromtimestamp(float(exp)),
            iat=datetime.fromtimestamp(float(iat)),
            jti=str(jti) if jti else "",
            token_type=str(token_type) if token_type else "",
            user_id=int(user_id)
        )

    except (JWTError, ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="auth.invalid_token"
        )

    return token