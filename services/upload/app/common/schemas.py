from dataclasses import dataclass
from datetime import datetime

@dataclass(frozen=True, slots=True)
class TokenData:
  token_type: str
  exp: datetime
  iat: datetime
  jti: str
  user_id: int