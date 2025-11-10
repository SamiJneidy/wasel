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
    data = await branch_service.get_branches_for_organization()
    return ObjectListResponse(data=data)


@router.get(
    path="/{id}",
    response_model=SingleObjectResponse[BranchOut],
    # responses=RESPONSES["get_branch"],
    # summary=SUMMARIES["get_branch"],
    # description=DOCSTRINGS["get_branch"],
)
async def get_branch(
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
    # responses=RESPONSES["create_branch"],
    # summary=SUMMARIES["create_branch"],
    # description=DOCSTRINGS["create_branch"],
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
    # responses=RESPONSES["update_branch"],
    # summary=SUMMARIES["update_branch"],
    # description=DOCSTRINGS["update_branch"],
)
async def update_branch(
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
    # responses=RESPONSES["delete_branch"],
    # summary=SUMMARIES["delete_branch"],
    # description=DOCSTRINGS["delete_branch"],
)
async def delete_branch(
    id: int,
    branch_service: Annotated[BranchService, Depends(get_branch_service)],
    current_user: Annotated[UserOut, Depends(get_current_user)],
) -> None:
    return await branch_service.delete_branch(id)
