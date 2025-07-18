from fastapi import Depends
from .utils import EmailService
from src.core.config import settings


def get_email_service() -> EmailService:
    """Returns email service dependency"""
    return EmailService()
