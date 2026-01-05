from math import ceil
from fastapi import APIRouter, status
from src.core.dependencies.shared import get_current_user
from src.core.schemas import (
    PaginatedResponse,
    PagintationParams,
    SingleObjectResponse,
)
from src.docs.items import DOCSTRINGS, RESPONSES, SUMMARIES
from src.users.schemas import UserInDB
from .dependencies import Annotated, Depends, ZatcaPhase2Service, get_zatca_phase2_service
from .schemas import ZatcaPhase2BranchDataCreate, ZatcaPhase2BranchDataOut
from .services import ZatcaPhase2Service

router = APIRouter(
    prefix="/zatca",
    tags=["Zatca"],
)


# =========================================================
# GET routes
# =========================================================

@router.get(
    path="/{id}",
    response_model=SingleObjectResponse[ZatcaPhase2BranchDataOut],
    # responses=RESPONSES["get_item"],
    # summary=SUMMARIES["get_item"],
    # description=DOCSTRINGS["get_item"],
)
async def get_branch_metadata(
    id: int,
    zatca_service: Annotated[ZatcaPhase2Service, Depends(get_zatca_phase2_service)],
    current_user: Annotated[UserInDB, Depends(get_current_user)],
) -> SingleObjectResponse[ZatcaPhase2BranchDataOut]:
    data = await zatca_service.get_branch_tax_authority_data(current_user, id)
    return SingleObjectResponse(data=data)


# =========================================================
# POST routes
# =========================================================

@router.post(
    path="/branches/{branch_id}",
    status_code=status.HTTP_201_CREATED,
    response_model=SingleObjectResponse[ZatcaPhase2BranchDataOut],
    # responses=RESPONSES["create_item"],
    # summary=SUMMARIES["create_item"],
    # description=DOCSTRINGS["create_item"],
)
async def create_metadata(
    branch_id: int,
    body: ZatcaPhase2BranchDataCreate,
    zatca_service: Annotated[ZatcaPhase2Service, Depends(get_zatca_phase2_service)],
    current_user: Annotated[UserInDB, Depends(get_current_user)],
) -> SingleObjectResponse[ZatcaPhase2BranchDataOut]:
    data = await zatca_service.create_branch_metadata(current_user, branch_id, body)
    return SingleObjectResponse(data=data)


# =========================================================
# PATCH routes
# =========================================================

# @router.patch(
#     path="/{id}",
#     response_model=SingleObjectResponse[ItemOut],
#     responses=RESPONSES["update_item"],
#     summary=SUMMARIES["update_item"],
#     description=DOCSTRINGS["update_item"],
# )
# async def update_item(
#     id: int,
#     body: ItemUpdate,
#     item_service: Annotated[ItemService, Depends(get_item_service)],
#     current_user: Annotated[UserInDB, Depends(get_current_user)],
# ) -> SingleObjectResponse[ItemOut]:
#     data = await item_service.update(current_user, id, body)
#     return SingleObjectResponse(data=data)


# # =========================================================
# # DELETE routes
# # =========================================================

# @router.delete(
#     path="/{id}",
#     status_code=status.HTTP_204_NO_CONTENT,
#     responses=RESPONSES["delete_item"],
#     summary=SUMMARIES["delete_item"],
#     description=DOCSTRINGS["delete_item"],
# )
# async def delete_item(
#     id: int,
#     item_service: Annotated[ItemService, Depends(get_item_service)],
#     current_user: Annotated[UserInDB, Depends(get_current_user)],
# ) -> None:
#     return await item_service.delete(current_user, id)
