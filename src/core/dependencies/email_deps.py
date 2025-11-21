from fastapi import Depends
from typing import Annotated
from ..services.email_service import EmailService

def get_email_service() -> EmailService:
    return EmailService()
