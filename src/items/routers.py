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

router = APIRouter(
    prefix="/items",
    tags=["Items"],
)


@router.post(
    path="/",
    response_model=SingleObjectResponse[ItemOut],
)
async def create_item(
    body: ItemCreate,
    item_service: Annotated[ItemService, Depends(get_item_service)],
    current_user: Annotated[UserOut, Depends(get_current_user)],
) -> ItemOut:
    """Create a new item."""
    data = await item_service.create(body)
    return SingleObjectResponse(data=data)


@router.patch(
    path="/{id}",
    response_model=SingleObjectResponse[ItemOut],
)
async def update_item(
    id: int,
    body: ItemUpdate,
    item_service: Annotated[ItemService, Depends(get_item_service)],
    current_user: Annotated[UserOut, Depends(get_current_user)],
) -> ItemOut:
    """Update a item."""
    data = await item_service.update(id, body)
    return SingleObjectResponse(data=data)


@router.delete(
    path="/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_item(
    id: int,
    item_service: Annotated[ItemService, Depends(get_item_service)],
    current_user: Annotated[UserOut, Depends(get_current_user)],
) -> None:
    """Delete a item."""
    return await item_service.delete(id)


@router.get(
    path="/",
    response_model=ObjectListResponse[ItemOut],
)
async def get_items_for_user(
    item_service: Annotated[ItemService, Depends(get_item_service)],
    current_user: Annotated[UserOut, Depends(get_current_user)],
) -> ObjectListResponse[ItemOut]:
    """Delete a item."""
    data = await item_service.get_items_for_user()
    return ObjectListResponse(data=data)


@router.get(
    path="/{id}",
    response_model=SingleObjectResponse[ItemOut]
)
async def get_item(
    id: int,
    item_service: Annotated[ItemService, Depends(get_item_service)],
    current_user: Annotated[UserOut, Depends(get_current_user)],
) -> ItemOut:
    """Get a signle item."""
    data = await item_service.get(id)
    return SingleObjectResponse(data=data)