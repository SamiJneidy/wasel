from fastapi import Depends
from sqlalchemy.orm import Session
from typing import Annotated
from .schemas import UserOut
from .repositories import UserRepository
from .services import UserService
from src.core.database import get_db
from src.core.dependencies import EmailService, get_email_service

def get_user_repository(db: Annotated[Session, Depends(get_db)]) -> UserRepository:
    """Returns user repository dependency."""
    return UserRepository(db)

def get_user_service(
    user_repo: Annotated[UserRepository, Depends(get_user_repository)],
    email_service: Annotated[EmailService, Depends(get_email_service)],
) -> UserService:
    """Returns otp service dependency"""
    return UserService(user_repo, email_service)
