from fastapi import Request, Depends
from typing import Annotated
from src.core.enums import TokenScope
from src.users.schemas import UserOut
from src.users.dependencies.services import UserService, get_user_service
from src.auth.dependencies.token_deps import TokenService, get_token_service
from src.auth.exceptions import InvalidTokenException

async def get_access_token_payload(
    request: Request,
    token_service: Annotated[TokenService, Depends(get_token_service)],
) -> dict:
    token = request.cookies.get("access_token", "NO_TOKEN")
    payload = token_service.decode_token(token)
    if payload["scope"] != TokenScope.ACCESS:
        raise InvalidTokenException(detail="Token scope is not ACCESS")
    return payload

async def get_current_user(
    token_payload: dict = Depends(get_access_token_payload),
    user_service: UserService = Depends(get_user_service)
) -> UserOut:
    """Returns the current user logged in."""
    user_id: int = int(token_payload.get("sub"))
    return await user_service.get_user(user_id)