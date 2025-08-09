from pydantic_settings import BaseSettings, SettingsConfigDict
from fastapi_mail import ConnectionConfig

class Settings(BaseSettings):
    MAX_RETRIES: int
    TIMEOUT: int
    ZATCA_SIMPLIFIED_INVOICE_URL: str
    ZATCA_STANDARD_INVOICE_URL: str
    ZATCA_COMPLIANCE_INVOICE_URL: str
    ZATCA_PRODUCTION_CSID_RENEWAL_URL: str
    ZATCA_PRODUCTION_CSID_URL: str
    ZATCA_COMPLIANCE_CSID_URL: str
    ZATCA_ASN_TEMPLATE: str
    ENVIRONMENT: str
    MAXIMUM_NUMBER_OF_INVALID_LOGIN_ATTEMPTS: int
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRATION_MINUTES: int
    REFRESH_TOKEN_EXPIRATION_DAYS: int
    PASSWORD_RESET_OTP_EXPIRATION_MINUTES: int
    EMAIL_VERIFICATION_OTP_EXPIRATION_MINUTES: int
    DB_NAME: str
    DB_PASSWORD: str
    DB_USERNAME: str
    DB_HOSTNAME: str
    DB_PORT: int
    SQLALCHEMY_URL: str
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: str
    MAIL_PORT: int
    MAIL_SERVER: str
    REDIS_URL: str
    CLOUDINARY_CLOUD_NAME: str
    CLOUDINARY_API_KEY: str
    CLOUDINARY_API_SECRET: str
    CLOUDINARY_URL: str
    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()

mail_config = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
)