import jwt
from datetime import datetime, timedelta, timezone
from fastapi import Response
from src.core.enums import OTPStatus, OTPUsage, UserRole, UserStatus
from src.users.schemas import UserInDB, UserOut
from src.core.config import settings
from src.core.utils import EmailService
from src.users.services import UserService
from .otp import OTPService
from ..repositories import AuthenticationRepository
from ..utils import hash_password, verify_password
from ..schemas import (
    LoginRequest,
    LoginResponse,
    OTPCreate,
    SignUp, 
    SignUpResponse,
    VerifyEmailRequest,
    VerifyEmailResponse,
    ResetPasswordRequest,
    ResetPasswordResponse,
    RequestEmailVerificationOTPRequest,
    RequestEmailVerificationOTPResponse,
    RequestPasswordResetOTPRequest,
    RequestPasswordResetOTPResponse,
    VerifyPasswordResetOTPRequest,
    VerifyPasswordResetOTPResponse,
    TokenPayload,
    TokenRefreshRequest,
    TokenResponse,
    OTPOut,
    SignUpCompleteRequest,
    SignUpCompleteResponse,

)
from ..exceptions import (
    InvalidCredentialsException,
    InvalidTokenException,
    EmailAlreadyInUseException,
    UserNotActiveException, 
    UserNotFoundException,
    PasswordResetNotAllowedException,
    InvalidOTPException,
    UserBlockedException,
    UserDisabledException,
    UserNotVerifiedException,
)


class AuthService:
    def __init__(self, authentication_repo: AuthenticationRepository, user_service: UserService, otp_service: OTPService, email_service: EmailService) -> None:
        self.authentication_repo = authentication_repo
        self.user_service = user_service
        self.otp_service = otp_service
        self.email_service = email_service

    
    async def signup(self, data: SignUp) -> SignUpResponse:
        """Sign up a new user using email and password. Any extra user fields can be updated from the user service in 'users' package."""
        try:
            user = await self.user_service.get_by_email(data.email)
            raise EmailAlreadyInUseException()
        except UserNotFoundException:
            pass
        
        data.password = hash_password(data.password)
        user_dict: dict = data.model_dump(exclude={"confirm_password"})
        user_dict.update({"role": UserRole.CLIENT, "status": UserStatus.PENDING})
        user = await self.user_service.create_user_after_signup(user_dict)
        
        email_verification_otp_request = RequestEmailVerificationOTPRequest(email=data.email)
        await self.request_email_verification_otp(email_verification_otp_request)
        
        return SignUpResponse.model_validate(user)


    async def sign_up_complete(self, email: str, data: SignUpCompleteRequest) -> SignUpCompleteResponse:
        """Complete the signup process after verifying the email."""
        
        data_dict = data.model_dump()
        data_dict.update({"common_name": data.registraion_name, "organization_name": data.registraion_name, "country_code": "SA"})
        
        if data.vat_number[10] == "1":
            tin_number = data.vat_number[:10]
            data_dict.update({"organization_unit_name": tin_number})    
        else:
            data_dict.update({"organization_unit_name": data.registraion_name})

        db_user = await self.user_service.update_by_email(email, data_dict)
        
        return SignUpCompleteResponse.model_validate(db_user)
        

    async def login(self, credentials: LoginRequest) -> LoginResponse:
        db_user = await self.user_service.get_user_in_db(credentials.email)
        
        if db_user.status == UserStatus.DISABLED:
            raise UserDisabledException()
        if db_user.status == UserStatus.BLOCKED:
            raise UserBlockedException()
        if db_user.status == UserStatus.PENDING:
            raise UserNotVerifiedException()
        if db_user.status != UserStatus.ACTIVE:
            raise UserNotActiveException()
        
        if not verify_password(credentials.password, db_user.password):
            
            db_user: UserInDB = await self.user_service.increment_invlaid_login_attempts(credentials.email)
            if db_user.invalid_login_attempts >= settings.MAXIMUM_NUMBER_OF_INVALID_LOGIN_ATTEMPTS:
                await self.user_service.update_user_status(credentials.email, UserStatus.DISABLED)

            raise InvalidCredentialsException()
        
        token_payload = TokenPayload(sub=credentials.email)
        access_token = self.create_access_token(token_payload)
        refresh_token = self.create_refresh_token(token_payload)
        
        await self.user_service.reset_invalid_login_attempts(credentials.email)
        await self.user_service.update_last_login(credentials.email, datetime.utcnow())
        
        return LoginResponse(access_token=access_token, refresh_token=refresh_token)


    async def request_email_verification_otp(self, data: RequestEmailVerificationOTPRequest) -> RequestEmailVerificationOTPResponse:
        """Creates an OTP code for email verification and sends it to the email. This function will not work for blocked users."""
        
        user = await self.user_service.get_by_email(data.email)
        if user.status == UserStatus.BLOCKED:
            raise UserBlockedException()
        if user.status == UserStatus.DISABLED:
            raise UserDisabledException()
        
        expires_at = datetime.utcnow() + timedelta(minutes=settings.EMAIL_VERIFICATION_OTP_EXPIRATION_MINUTES)
        otp_data = OTPCreate(email=data.email, usage=OTPUsage.EMAIL_VERIFICATION, expires_at=expires_at)
        otp = await self.otp_service.create_otp(otp_data)
        
        await self.email_service.send_email_verification_otp(data.email, otp.code)
        
        return RequestEmailVerificationOTPResponse(email=data.email)
    

    async def request_password_reset_otp(self, data: RequestPasswordResetOTPRequest) -> RequestPasswordResetOTPResponse:
        """Request an OTP code for password reset."""
        
        user = await self.user_service.get_user_in_db(data.email)
        if user.status == UserStatus.PENDING:
            raise UserNotVerifiedException()
        if user.status == UserStatus.BLOCKED:
            raise UserBlockedException()
        
        expires_at = datetime.utcnow() + timedelta(minutes=settings.PASSWORD_RESET_OTP_EXPIRATION_MINUTES)
        otp_data = OTPCreate(email=data.email, usage=OTPUsage.PASSWORD_RESET, expires_at=expires_at)
        otp = await self.otp_service.create_otp(otp_data)
        
        await self.email_service.send_password_reset_otp(data.email, otp.code)
        
        return RequestPasswordResetOTPResponse(email=data.email)


    async def verify_email_verification_otp(self, data: VerifyEmailRequest) -> VerifyEmailResponse:
        """Verifies an email verification OTP code."""
        
        otp: OTPOut = await self.otp_service.get_otp_by_code(data.code)
        if otp.usage != OTPUsage.EMAIL_VERIFICATION or otp.email != data.email:
            raise InvalidOTPException()
        
        await self.otp_service.verify_otp(otp.code)
        await self.user_service.update_user_status(data.email, UserStatus.ACTIVE)
        
        return VerifyEmailResponse(email=data.email)    


    async def verify_password_reset_otp(self, data: VerifyPasswordResetOTPRequest) -> VerifyPasswordResetOTPResponse:
        """Verifies a password reste OTP code."""

        otp: OTPOut = await self.otp_service.get_otp_by_code(data.code)
        if otp.usage != OTPUsage.PASSWORD_RESET or data.email != otp.email:
            raise InvalidOTPException()

        await self.otp_service.verify_otp(otp.code)

        return VerifyPasswordResetOTPResponse(email=data.email)


    async def verify_email_after_signup(self, data: VerifyEmailRequest) -> TokenResponse:
        """Verifies email account after signup. The function will create access and refresh token after finishing the verificaion successfully."""
        
        await self.verify_email_verification_otp(data)
        
        token_payload = TokenPayload(sub=data.email)
        access_token = self.create_access_token(token_payload)
        refresh_token = self.create_refresh_token(token_payload)
        
        await self.user_service.reset_invalid_login_attempts(data.email)
        await self.user_service.update_last_login(data.email, datetime.utcnow())
        
        return TokenResponse(access_token=access_token, refresh_token=refresh_token)
    

    async def reset_password(self, data: ResetPasswordRequest) -> ResetPasswordResponse:
        """Resets the password for a user. The user needs to have a verified OTP code that is not expired to reset his password."""
        
        otp: OTPOut = await self.otp_service.get_otp_by_email_and_usage(data.email, OTPUsage.PASSWORD_RESET)
        if not otp or otp.status != OTPStatus.VERIFIED or otp.email != data.email or await self.otp_service.otp_is_expired(otp.code):
            raise PasswordResetNotAllowedException()
        
        hashed_password = hash_password(data.password)
        user = await self.user_service.update_by_email(data.email, data={"password": hashed_password})
        
        await self.user_service.reset_invalid_login_attempts(data.email)
        await self.user_service.update_user_status(data.email, UserStatus.ACTIVE)
        
        return ResetPasswordResponse(email=data.email)


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
            
            user = await self.user_service.get_by_email(email)
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
                samesite="lax",
                max_age=settings.REFRESH_TOKEN_EXPIRATION_DAYS * 24 * 60 * 60,
                path=path
            )
        if settings.ENVIRONMENT == "DEVELOPMENT":
            response.set_cookie(
                key="refresh_token",
                value=refresh_token,
                httponly=True,
                secure=False,
                samesite="lax",
                max_age=settings.REFRESH_TOKEN_EXPIRATION_DAYS * 24 * 60 * 60,
                path="/"
            )
