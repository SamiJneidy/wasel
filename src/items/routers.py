from fastapi import APIRouter, status
from .services import ItemService
from .schemas import (
    ItemCreate,
    ItemUpdate,
    ItemOut,
    UserOut,
    ObjectListResponse,
    SingleObjectResponse,
)
from .dependencies import (
    Annotated,
    Depends,
    get_item_service,
    get_current_user,
)
from src.docs.items import RESPONSES, DOCSTRINGS, SUMMARIES

router = APIRouter(
    prefix="/items",
    tags=["Items"],
)


@router.post(
    path="/",
    status_code=status.HTTP_201_CREATED,
    response_model=SingleObjectResponse[ItemOut],
    responses=RESPONSES["create_item"],
    summary=SUMMARIES["create_item"],
    description=DOCSTRINGS["create_item"],
)
async def create_item(
    body: ItemCreate,
    item_service: Annotated[ItemService, Depends(get_item_service)],
    current_user: Annotated[UserOut, Depends(get_current_user)],
) -> ItemOut:
    data = await item_service.create(body)
    return SingleObjectResponse(data=data)


@router.patch(
    path="/{id}",
    response_model=SingleObjectResponse[ItemOut],
    responses=RESPONSES["update_item"],
    summary=SUMMARIES["update_item"],
    description=DOCSTRINGS["update_item"],
)
async def update_item(
    id: int,
    body: ItemUpdate,
    item_service: Annotated[ItemService, Depends(get_item_service)],
    current_user: Annotated[UserOut, Depends(get_current_user)],
) -> ItemOut:
    data = await item_service.update(id, body)
    return SingleObjectResponse(data=data)


@router.delete(
    path="/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses=RESPONSES["delete_item"],
    summary=SUMMARIES["delete_item"],
    description=DOCSTRINGS["delete_item"],
)
async def delete_item(
    id: int,
    item_service: Annotated[ItemService, Depends(get_item_service)],
    current_user: Annotated[UserOut, Depends(get_current_user)],
) -> None:
    return await item_service.delete(id)


@router.get(
    path="/",
    response_model=ObjectListResponse[ItemOut],
    responses=RESPONSES["get_items_for_user"],
    summary=SUMMARIES["get_items_for_user"],
    description=DOCSTRINGS["get_items_for_user"],
)
async def get_items_for_user(
    item_service: Annotated[ItemService, Depends(get_item_service)],
    current_user: Annotated[UserOut, Depends(get_current_user)],
) -> ObjectListResponse[ItemOut]:
    data = await item_service.get_items_for_user()
    return ObjectListResponse(data=data)


@router.get(
    path="/{id}",
    response_model=SingleObjectResponse[ItemOut],
    responses=RESPONSES["get_item"],
    summary=SUMMARIES["get_item"],
    description=DOCSTRINGS["get_item"],
)
async def get_item(
    id: int,
    item_service: Annotated[ItemService, Depends(get_item_service)],
    current_user: Annotated[UserOut, Depends(get_current_user)],
) -> ItemOut:
    data = await item_service.get(id)
    return SingleObjectResponse(data=data)