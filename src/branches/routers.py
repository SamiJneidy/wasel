from typing import Annotated

from fastapi import APIRouter, status, Depends

from .services import BranchService
from src.users.schemas import UserInDB
from .schemas import (
    BranchCreate,
    BranchUpdate,
    BranchOut,
    ObjectListResponse,
    SingleObjectResponse,
)
from .dependencies import get_branch_service
from src.core.dependencies.shared import get_current_user
from src.docs.branches import RESPONSES, DOCSTRINGS, SUMMARIES

router = APIRouter(
    prefix="/branches",
    tags=["Branches"],
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
    current_user: Annotated[UserInDB, Depends(get_current_user)],
) -> ObjectListResponse[BranchOut]:
    data = await branch_service.get_branches_for_organization(current_user)
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
    current_user: Annotated[UserInDB, Depends(get_current_user)],
) -> SingleObjectResponse[BranchOut]:
    data = await branch_service.get_branch(current_user, id)
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
    current_user: Annotated[UserInDB, Depends(get_current_user)],
) -> SingleObjectResponse[BranchOut]:
    data = await branch_service.create_branch(current_user, body)
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
    current_user: Annotated[UserInDB, Depends(get_current_user)],
) -> SingleObjectResponse[BranchOut]:
    data = await branch_service.update_branch(current_user, id, body)
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
    current_user: Annotated[UserInDB, Depends(get_current_user)],
) -> None:
    await branch_service.delete_branch(current_user, id)
    return None
