
from fastapi import Depends
from .auth import get_current_user
from src.users.schemas import UserOut
from src.authorization.dependencies import AuthorizationService, get_authorization_service
from src.authorization.exceptions import PermissionDeniedException


def require_permission(resource: str, action: str):
    """Dependency to require a specific permission for the current user."""
    async def checker(
        current_user: UserOut = Depends(get_current_user), 
        authorization_service: AuthorizationService = Depends(get_authorization_service)
    ) -> None:
        has_permission = await authorization_service.user_has_permission(current_user.organization_id, current_user.id, resource, action)
        if not has_permission:
            raise PermissionDeniedException(detail=f"Permission denied! Resource: {resource}, Action: {action}")
    return checker