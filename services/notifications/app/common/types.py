import uuid
from typing import Annotated
from fastapi import Depends, HTTPException, Header
from jose import JWTError
from app.core.security import decode_token

class UserTokenType:
    def __init__(self, user_id: int):
        self.user_id = user_id

async def get_current_user(authorization: Annotated[str | None, Header()] = None) -> UserTokenType:
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization header")
    
    try:
        token = authorization.split(" ")[1]
        payload = decode_token(token)
        user_id = payload.get("user_id")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token: user_id missing")
        return UserTokenType(user_id=int(user_id))
    except (JWTError, ValueError, TypeError) as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")
