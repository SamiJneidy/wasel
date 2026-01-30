from fastapi import Depends, Request
from fastapi.security import OAuth2PasswordBearer
from typing import Annotated
from src.auth.exceptions import InvalidTokenException
from src.core.enums import TokenScope
from src.auth.services.token_service import TokenService
from src.users.schemas import UserOut
from src.branches.schemas import BranchOut
from src.organizations.schemas import OrganizationOut
from src.auth.dependencies.token_deps import TokenService, get_token_service
from src.users.dependencies import get_user_service, UserService
from src.branches.dependencies.repositories import BranchRepository, get_branch_repository
from src.organizations.dependencies import OrganizationRepository, get_organization_repository
from src.users.exceptions import UserNotFoundException
from src.branches.exceptions import BranchNotFoundException
from src.organizations.exceptions import OrganizationNotFoundException
from src.core.schemas.context import RequestContext

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/swaggerlogin")

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
) -> UserOut | None:
    """Returns the current user logged in."""
    user_id: int = token_payload.get("sub")
    return await user_service.get_user(user_id)

async def get_current_branch(
    token_payload: dict = Depends(get_access_token_payload),
    branch_repo: BranchRepository = Depends(get_branch_repository)
) -> BranchOut:
    """Returns the current branch selected by the user."""
    branch_id: int = token_payload.get("branch_id")
    organization_id: int = token_payload.get("organization_id")
    branch = await branch_repo.get_branch(organization_id, branch_id)
    if not branch:
        raise BranchNotFoundException()
    return BranchOut.model_validate(branch)

async def get_current_organization(
    token_payload: dict = Depends(get_access_token_payload),
    organization_repo: OrganizationRepository = Depends(get_organization_repository)
) -> OrganizationOut:
    """Returns the current organization of the logged in user."""
    organization_id: int = token_payload.get("organization_id")
    organization = await organization_repo.get(organization_id)
    if not organization:
        raise OrganizationNotFoundException()
    return OrganizationOut.model_validate(organization)

async def get_request_context(
    current_user: UserOut = Depends(get_current_user),
    current_branch: BranchOut = Depends(get_current_branch),
    current_organization: OrganizationOut = Depends(get_current_organization),
) -> RequestContext:
    """Returns the context of the current request."""
    return RequestContext(user=current_user, branch=current_branch, organization=current_organization)

async def get_current_user_from_sign_up_complete_token(
    request: Request,
    token_service: Annotated[TokenService, Depends(get_token_service)],
    user_service: Annotated[UserService, Depends(get_user_service)]
) -> UserOut:
    """Returns the email of the current user waiting for sign up complete step."""
    token = request.cookies.get("sign_up_complete_token", "NO_TOKEN")
    payload = token_service.decode_token(token)
    if payload["scope"] != TokenScope.SIGN_UP_COMPLETE:
        raise InvalidTokenException(detail="Token scope is not SIGN_UP_COMPLETE")
    user_id: int = payload.get("user_id")
    return await user_service.get_user(user_id)


