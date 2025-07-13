from fastapi import APIRouter
from src.authentication.routers import router as authentication_router
from src.users.routers import router as users_router
v1_router = APIRouter(prefix="/api/v1")

v1_router.include_router(authentication_router)
v1_router.include_router(users_router)
