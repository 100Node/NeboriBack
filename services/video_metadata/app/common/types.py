from typing import Annotated

from fastapi import Depends

from app.common.dependencies import get_token_data
from app.common.schemas import TokenData

UserTokenType = Annotated[TokenData, Depends(get_token_data)]