from fastapi import APIRouter, status
from .services import BranchService
from .schemas import (
    BranchCreate,
    BranchUpdate,
    BranchOut,
    UserOut,
    ObjectListResponse,
    SingleObjectResponse,
)
from .dependencies import (
    Annotated,
    Depends,
    get_branch_service,
    get_current_user,
)
from src.docs.branches import RESPONSES, DOCSTRINGS, SUMMARIES

router = APIRouter(
    prefix="/branches",
    tags=["Branchs"],
)

@router.get(
    path="/",
    response_model=ObjectListResponse[BranchOut],
    # responses=RESPONSES["get_branches_for_user"],
    # summary=SUMMARIES["get_branches_for_user"],
    # description=DOCSTRINGS["get_branches_for_user"],
)
async def get_branches_for_organization(
    branch_service: Annotated[BranchService, Depends(get_branch_service)],
    current_user: Annotated[UserOut, Depends(get_current_user)],
) -> ObjectListResponse[BranchOut]:
    data = await branch_service.get_branches_for_organization(current_user.organization_id)
    return ObjectListResponse(data=data)


@router.get(
    path="/{id}",
    response_model=SingleObjectResponse[BranchOut],
    # responses=RESPONSES["get_organization"],
    # summary=SUMMARIES["get_organization"],
    # description=DOCSTRINGS["get_organization"],
)
async def get_organization(
    id: int,
    branch_service: Annotated[BranchService, Depends(get_branch_service)],
    current_user: Annotated[UserOut, Depends(get_current_user)],
) -> BranchOut:
    data = await branch_service.get_branch(id)
    return SingleObjectResponse(data=data)


@router.post(
    path="/",
    status_code=status.HTTP_201_CREATED,
    response_model=SingleObjectResponse[BranchOut],
    # responses=RESPONSES["create_organization"],
    # summary=SUMMARIES["create_organization"],
    # description=DOCSTRINGS["create_organization"],
)
async def create_branch(
    body: BranchCreate,
    branch_service: Annotated[BranchService, Depends(get_branch_service)],
    current_user: Annotated[UserOut, Depends(get_current_user)],
) -> BranchOut:
    data = await branch_service.create_branch(body)
    return SingleObjectResponse(data=data)


@router.patch(
    path="/{id}",
    response_model=SingleObjectResponse[BranchOut],
    # responses=RESPONSES["update_organization"],
    # summary=SUMMARIES["update_organization"],
    # description=DOCSTRINGS["update_organization"],
)
async def update_organization(
    id: int,
    body: BranchUpdate,
    branch_service: Annotated[BranchService, Depends(get_branch_service)],
    current_user: Annotated[UserOut, Depends(get_current_user)],
) -> BranchOut:
    data = await branch_service.update_branch(id, body)
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
    branch_service: Annotated[BranchService, Depends(get_branch_service)],
    current_user: Annotated[UserOut, Depends(get_current_user)],
) -> None:
    return await branch_service.delete_branch(id)
