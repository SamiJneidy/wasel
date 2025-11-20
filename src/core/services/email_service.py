import requests
from fastapi_mail import FastMail, MessageSchema
from pydantic import EmailStr
from src.core.config import mail_config, settings
from src.auth.exceptions import OTPCouldNotBeSentException
from ..exceptions.email_exceptions import EmailCouldNotBeSentException


class EmailService:
    def __init__(self):
        self.fastmail = FastMail(mail_config)


    async def send_email(self, to: list[EmailStr], subject: str, body: str, subtype: str = "plain") -> None:
        """Send an email for a list of emails."""
        try:
            message = MessageSchema(
                subject=subject, body=body, recipients=to, subtype=subtype
            )
            await self.fastmail.send_message(message)
        except Exception as e:
            raise EmailCouldNotBeSentException()
    
    async def send_email_verification_otp(self, email: str, code: str) -> None:
        """Send an OTP code for email verification."""
        await self.send_email(
            to=[email],
            subject="Email verification",
            body=f"Please use this code to verify your account: {code}",
        )
        

    async def send_password_reset_otp(self, email: str, code: str) -> None:
        """Send an OTP code for password reset."""
        await self.send_email(
            to=[email],
            subject="Password Reset",
            body=f"Please use this code to reset your password: {code}",
        )
    
    async def send_user_invitation(self, email: str, url: str) -> None:
        """Send an OTP code for password reset."""
        await self.send_email(
            to=[email],
            subject="Invite To Wasel",
            body=f"Please click on the following link to finsih your account setup: {url}. Don't share this link with anyone.",
        )