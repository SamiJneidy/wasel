import requests
from fastapi_mail import FastMail, MessageSchema
from pydantic import EmailStr
from src.core.config import mail_config
from src.auth.exceptions import OTPCouldNotBeSentException


class EmailService:
    def __init__(self):
        self.fastmail = FastMail(mail_config)


    async def send_email(self, to: list[EmailStr], subject: str, body: str, subtype: str = "plain") -> None:
        """Send an email for a list of emails."""
        message = MessageSchema(
            subject=subject, body=body, recipients=to, subtype=subtype
        )
        await self.fastmail.send_message(message)

    
    async def send_email_verification_otp(self, email: str, code: str) -> None:
        """Send an OTP code for email verification."""
        try:
            await self.send_email(
                to=[email],
                subject="Email verification",
                body=f"Please use this code to verify your account: {code}",
            )
        except Exception as e:
            raise OTPCouldNotBeSentException()
        

    async def send_password_reset_otp(self, email: str, code: str) -> None:
        """Send an OTP code for password reset."""
        try:
            await self.send_email(
                to=[email],
                subject="Password Reset",
                body=f"Please use this code to reset your password: {code}",
            )
        except Exception as e:
            raise OTPCouldNotBeSentException()