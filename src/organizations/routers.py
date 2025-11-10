from fastapi import APIRouter, status
from .services import OrganizationService
from .schemas import (
    OrganizationCreate,
    OrganizationUpdate,
    OrganizationOut,
    UserOut,
    ObjectListResponse,
    SingleObjectResponse,
)
from .dependencies import (
    Annotated,
    Depends,
    get_organization_service,
)
from src.core.dependencies import get_current_user
from src.docs.organizations import RESPONSES, DOCSTRINGS, SUMMARIES

router = APIRouter(
    prefix="/organizations",
    tags=["Organizations"],
)


@router.post(
    path="/",
    status_code=status.HTTP_201_CREATED,
    response_model=SingleObjectResponse[OrganizationOut],
    # responses=RESPONSES["create_organization"],
    # summary=SUMMARIES["create_organization"],
    # description=DOCSTRINGS["create_organization"],
)
async def create_organization(
    body: OrganizationCreate,
    organization_service: Annotated[OrganizationService, Depends(get_organization_service)],
    current_user: Annotated[UserOut, Depends(get_current_user)],
) -> OrganizationOut:
    data = await organization_service.create_organization(body)
    return SingleObjectResponse(data=data)


@router.patch(
    path="/{id}",
    response_model=SingleObjectResponse[OrganizationOut],
    # responses=RESPONSES["update_organization"],
    # summary=SUMMARIES["update_organization"],
    # description=DOCSTRINGS["update_organization"],
)
async def update_organization(
    id: int,
    body: OrganizationUpdate,
    organization_service: Annotated[OrganizationService, Depends(get_organization_service)],
    current_user: Annotated[UserOut, Depends(get_current_user)],
) -> OrganizationOut:
    data = await organization_service.update_organization(id, body)
    return SingleObjectResponse(data=data)


@router.delete(
    path="/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    # responses=RESPONSES["delete_organization"],
    # summary=SUMMARIES["delete_organization"],
    # description=DOCSTRINGS["delete_organization"],
)
async def delete_organization(
    id: int,
    organization_service: Annotated[OrganizationService, Depends(get_organization_service)],
    current_user: Annotated[UserOut, Depends(get_current_user)],
) -> None:
    return await organization_service.delete_organization(id)


@router.get(
    path="/{id}",
    response_model=SingleObjectResponse[OrganizationOut],
    # responses=RESPONSES["get_organization"],
    # summary=SUMMARIES["get_organization"],
    # description=DOCSTRINGS["get_organization"],
)
async def get_organization(
    id: int,
    organization_service: Annotated[OrganizationService, Depends(get_organization_service)],
    current_user: Annotated[UserOut, Depends(get_current_user)],
) -> OrganizationOut:
    data = await organization_service.get_organization(id)
    return SingleObjectResponse(data=data)