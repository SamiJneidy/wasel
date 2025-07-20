from fastapi import APIRouter
from src.auth.routers import router as auth_router
from src.users.routers import router as users_router
from src.csid.routers import router as csid_router

v1_router = APIRouter(prefix="/api/v1")

v1_router.include_router(auth_router)
v1_router.include_router(users_router)
v1_router.include_router(csid_router)
