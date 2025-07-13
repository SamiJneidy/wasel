import jwt
from datetime import datetime, timedelta, timezone
from fastapi import Response
from src.core.enums import OTPStatus, OTPUsage, UserRole, UserStatus
from src.users.schemas import UserOut
from .repositories import OTPRepository, AuthenticationRepository, UserRepository
from src.core.config import settings
from src.core.utils import send_email
from .utils import hash_password, verify_password, generate_random_code
from .schemas import (
    LoginResponse,
    OTPCreate,
    OTPOut,
    OTPVerificationRequest,
    OTPVerificationResponse,
    PasswordResetRequest, 
    PasswordResetResponse, 
    PasswordResetOTPRequest,
    PasswordResetOTPResponse,
    TokenPayload,
    TokenRefreshRequest,
    TokenResponse,
    SignUp, 
    SignUpResponse,
    Login,
    EmailVerificationOTPRequest,
    EmailVerificationOTPResponse,
)
from .exceptions import (
    InvalidCredentialsException,
    InvalidTokenException,
    EmailAlreadyInUseException,
    UserNotActiveException, 
    UserNotFoundException,
    PasswordResetNotAllowedException, 
    PasswordsDontMatchException,
    OTPNotFoundException,
    InvalidOTPException,
    ExpiredOTPException,
    OTPAlreadyUsedException,
    OTPCouldNotBeSentException,
    UserBlockedException,
    UserDisabledException,
    UserNotVerifiedException,
)


class OTPService:
    def __init__(self, otp_repo: OTPRepository, user_repo: UserRepository):
        self.otp_repo = otp_repo
        self.user_repo = user_repo

    async def get_otp_by_code(self, code: str) -> OTPOut:
        """Returns OTP by code."""
        db_otp = await self.otp_repo.get_otp_by_code(code)
        if not db_otp:
            raise InvalidOTPException()
        return OTPOut.model_validate(db_otp)

    async def get_otp_by_email_and_usage(self, email: str, usage: OTPUsage) -> OTPOut:
        """Returns OTP by email and usage."""
        db_otp = await self.otp_repo.get_otp_by_email_and_usage(email, usage)
        if not db_otp:
            raise InvalidOTPException()
        return OTPOut.model_validate(db_otp)

    async def generate_otp(self) -> str:
        """Generates a unique OTP code."""
        while True:
            code: str = generate_random_code()
            code_count: int = await self.otp_repo.get_code_count(code)
            if code_count == 0:
                break
        return code
    
    async def create_otp_for_email_verification(self, email: str) -> OTPOut:
        """Creates an OTP code for email verification and sends it to the email. This function will not work for blocked users."""
        user = await self.user_repo.get_by_email(email)
        if not user:
            raise UserNotFoundException()
        if user.status == UserStatus.BLOCKED:
            raise UserBlockedException()
        await self.otp_repo.revoke_otp_codes_for_user(email, OTPUsage.EMAIL_VERIFICATION)
        code = await self.generate_otp()
        expires_at = datetime.now() + timedelta(minutes=settings.EMAIL_VERIFICATION_OTP_EXPIRATION_MINUTES)
        otp_data = OTPCreate(
            email=email, code=code, usage=OTPUsage.EMAIL_VERIFICATION, status=OTPStatus.PENDING, expires_at=expires_at
        )
        db_otp = await self.otp_repo.create_otp(otp_data.model_dump())
        await self.send_otp_for_email_verification(email, code)
        return OTPOut.model_validate(db_otp)

    async def create_otp_for_password_reset(self, email: str) -> OTPOut:
        """Creates an OTP code for password reset and sends it to the email."""
        user = await self.user_repo.get_by_email(email)
        if not user:
            raise UserNotFoundException()
        if user.status == UserStatus.BLOCKED:
            raise UserBlockedException()
        await self.otp_repo.revoke_otp_codes_for_user(email, OTPUsage.PASSWORD_RESET)
        code = await self.generate_otp()
        expires_at = datetime.now() + timedelta(minutes=settings.PASSWORD_RESET_OTP_EXPIRATION_MINUTES)
        otp_data = OTPCreate(
            email=email, code=code, usage=OTPUsage.PASSWORD_RESET, status=OTPStatus.PENDING, expires_at=expires_at
        )
        db_otp = await self.otp_repo.create_otp(otp_data.model_dump())
        await self.send_otp_for_password_reset(email, code)
        return OTPOut.model_validate(db_otp)

    async def otp_is_expired(self, code: str) -> bool:
        """Checks if an OTP code is expired or not."""
        db_otp = await self.otp_repo.get_otp_by_code(code)
        if db_otp.expires_at < datetime.now():
            return True
        return False

    async def verify_otp(self, otp: OTPVerificationRequest) -> OTPVerificationResponse:
        """Uses an OTP code to complete the verification process for any usage. The code will no longer be valid after using it."""
        db_otp = await self.otp_repo.get_otp_by_code(otp.code)
        if db_otp is None:
            raise InvalidOTPException()
        if await self.otp_is_expired(otp.code):
            raise InvalidOTPException()
        if db_otp.status == OTPStatus.EXPIRED or db_otp.status == OTPStatus.VERIFIED:
            raise InvalidOTPException()
        db_otp = await self.otp_repo.verify_otp(otp.code)
        user = await self.user_repo.get_by_email(db_otp.email)
        if db_otp.usage == OTPUsage.EMAIL_VERIFICATION and user.status == UserStatus.PENDING:
            await self.user_repo.update_user_status(db_otp.email, UserStatus.ACTIVE)
        if db_otp.usage == OTPUsage.PASSWORD_RESET and user.status == UserStatus.DISABLED:
            await self.user_repo.update_user_status(db_otp.email, UserStatus.ACTIVE)
        return OTPVerificationResponse(email=db_otp.email)

    async def send_otp_for_email_verification(self, email: str, code: str) -> None:
        """Send an OTP code for email verification."""
        try:
            await send_email(
                to=[email],
                subject="Email verification",
                body=f"Please use this code to verify your account: {code}",
            )
        except Exception as e:
            raise OTPCouldNotBeSentException()
        
    async def send_otp_for_password_reset(self, email: str, code: str) -> None:
        """Send an OTP code for password reset."""
        try:
            await send_email(
                to=[email],
                subject="Password Reset",
                body=f"Please use this code to reset your password: {code}",
            )
        except Exception as e:
            raise OTPCouldNotBeSentException()



class AuthenticationService:
    def __init__(self, authentication_repo: AuthenticationRepository, user_repo: UserRepository, otp_service: OTPService) -> None:
        self.authentication_repo = authentication_repo
        self.user_repo = user_repo
        self.otp_service = otp_service

    async def signup(self, data: SignUp) -> SignUpResponse:
        """Sign up a new user using email and password. Any extra user fields can be updated from the user service in 'users' package."""
        user = await self.user_repo.get_by_email(data.email)
        if user:
            raise EmailAlreadyInUseException()
        
        data.password = hash_password(data.password)
        user_dict: dict = data.model_dump(exclude={"confirm_password"})
        user_dict.update({"role": UserRole.ADMIN, "status": UserStatus.PENDING})
        db_user = await self.user_repo.create(user_dict)
        
        await self.otp_service.create_otp_for_email_verification(email=data.email)
        
        return SignUpResponse.model_validate(db_user)

    async def login(self, credentials: Login) -> LoginResponse:
        db_user = await self.user_repo.get_by_email(credentials.email)
        
        if not db_user:
            raise UserNotFoundException()
        if db_user.status == UserStatus.DISABLED:
            raise UserDisabledException()
        if db_user.status == UserStatus.BLOCKED:
            raise UserBlockedException()
        if db_user.status == UserStatus.PENDING:
            raise UserNotVerifiedException()
        if db_user.status != UserStatus.ACTIVE:
            raise UserNotActiveException()
        
        if not verify_password(credentials.password, db_user.password):
            db_user = await self.user_repo.increment_invalid_login_attempts(credentials.email)
            if db_user.invalid_login_attempts >= settings.MAXIMUM_NUMBER_OF_INVALID_LOGIN_ATTEMPTS:
                await self.user_repo.update_user_status(credentials.email, UserStatus.DISABLED)
            raise InvalidCredentialsException()
        
        token_payload = TokenPayload(sub=credentials.email)
        access_token = self.create_access_token(token_payload)
        refresh_token = self.create_refresh_token(token_payload)
        
        await self.user_repo.reset_invalid_login_attempts(credentials.email)
        
        await self.user_repo.update_last_login(credentials.email, datetime.utcnow())
        
        return LoginResponse(access_token=access_token, refresh_token=refresh_token)

    async def request_password_reset(self, data: PasswordResetOTPRequest) -> PasswordResetOTPResponse:
        """Request an OTP code for password reset."""
        
        db_user = await self.user_repo.get_by_email(data.email)
        if not db_user:
            raise UserNotFoundException()
        if db_user.status == UserStatus.PENDING:
            raise UserNotVerifiedException()
        if db_user.status == UserStatus.BLOCKED:
            raise UserBlockedException()
        
        await self.otp_service.create_otp_for_password_reset(data.email)
        
        return PasswordResetOTPResponse(email=data.email)
    
    async def request_email_verification(self, data: EmailVerificationOTPRequest) -> EmailVerificationOTPResponse:
        """Request an OTP code for email verification."""
        
        db_user = await self.user_repo.get_by_email(data.email)
        if not db_user:
            raise UserNotFoundException()
        if db_user.status == UserStatus.DISABLED:
            raise UserDisabledException()
        if db_user.status == UserStatus.BLOCKED:
            raise UserBlockedException()
        
        await self.otp_service.create_otp_for_email_verification(data.email)
        
        return EmailVerificationOTPResponse(email=data.email)

    async def reset_password(self, data: PasswordResetRequest) -> PasswordResetResponse:
        """Reset the password after verifying the OTP code."""
        try:
            otp: OTPOut = await self.otp_service.get_otp_by_email_and_usage(data.email, OTPUsage.PASSWORD_RESET)
        except Exception as e:
            raise PasswordResetNotAllowedException()
        
        if await self.otp_service.otp_is_expired(otp.code):
            raise PasswordResetNotAllowedException()
        if otp.status != OTPStatus.VERIFIED or data.email != otp.email:
            raise PasswordResetNotAllowedException()
        
        hashed_password = hash_password(data.password)
        db_user = await self.user_repo.update_by_email(data.email, data={"password": hashed_password})
        # TO BE ADDED
        # await self.otp_service.
        
        return PasswordResetResponse(email=data.email)

    def create_access_token(self, token_payload: TokenPayload) -> str:
        """Creates an access token."""
        token_payload.iat = datetime.now(tz=timezone.utc)
        token_payload.exp = datetime.now(tz=timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRATION_MINUTES)
        to_encode = token_payload.model_dump()
        return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    def create_refresh_token(self, token_payload: TokenPayload) -> str:
        """Creates a refresh token."""
        token_payload.iat = datetime.now(tz=timezone.utc)
        token_payload.exp = datetime.now(tz=timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRATION_DAYS)
        to_encode = token_payload.model_dump()
        return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    
    async def verify_token(self, token: str) -> UserOut:
        """Verifies if a token is valid or not and returns the user if the token was valid."""
        try:
            payload_dict: dict = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            email = payload_dict.get("sub")
            
            if not email:
                raise InvalidTokenException()
            
            user = await self.user_repo.get_by_email(email)
            if not user:
                raise InvalidTokenException()
            
            return UserOut.model_validate(user)
        
        except jwt.InvalidTokenError:
            raise InvalidTokenException()

    async def get_user_from_token(self, token: str) -> UserOut:
        """Extracts user from a valid token."""
        user = await self.verify_token(token)
        return user
    
    async def refresh(self, token_refresh_request: TokenRefreshRequest) -> TokenResponse:
        """Refresh an expired access token using a valid refresh token and sets new refresh token in HTTP-only cookie."""
        user = await self.verify_token(token_refresh_request.refresh_token)
        token_payload = TokenPayload(sub=user.email)
        access_token = self.create_access_token(token_payload)
        refresh_token = self.create_refresh_token(token_payload)
        return TokenResponse(access_token=access_token, refresh_token=refresh_token)

    async def set_refresh_token_cookie(self, response: Response, refresh_token: str, path: str) -> None:
        """Sets the refresh token cookie. The cookie will be set based on the current environment. The 'path' argument will not be used in development environment."""
        if settings.ENVIRONMENT == "PRODUCTION":
            response.set_cookie(
                key="refresh_token",
                value=refresh_token,
                httponly=True,
                secure=True,
                samesite="Lax",
                max_age=settings.REFRESH_TOKEN_EXPIRATION_DAYS * 24 * 60 * 60,
                path=path
            )
        if settings.ENVIRONMENT == "DEVELOPMENT":
            response.set_cookie(
                key="refresh_token",
                value=refresh_token,
                httponly=True,
                secure=False,
                samesite="Lax",
                max_age=settings.REFRESH_TOKEN_EXPIRATION_DAYS * 24 * 60 * 60,
                path="/"
            )
