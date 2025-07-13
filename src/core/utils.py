from fastapi_mail import FastMail, MessageSchema
from pydantic import EmailStr
from src.core.config import mail_config

fastmail = FastMail(mail_config)

async def send_email(to: list[EmailStr], subject: str, body: str, subtype: str = "plain") -> None:
    message = MessageSchema(
        subject=subject, body=body, recipients=to, subtype=subtype
    )
    await fastmail.send_message(message)
