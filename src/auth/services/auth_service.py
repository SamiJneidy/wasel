from datetime import datetime, timedelta, timezone
from fastapi import Request, Response

from src.organizations.exceptions import OrganizationNotFoundException
from .token_service import TokenService
from src.core.enums import OTPStatus, OTPUsage, UserRole, UserStatus, UserType, ZatcaPhase2Stage
from src.core.services import EmailService
from src.users.schemas import UserInDB, UserOut
from src.core.config import settings
from src.users.services import UserService
from src.organizations.services import OrganizationService
from src.branches.services import BranchService
from .otp_service import OTPService
from ..repositories import AuthRepository
from ..utils import hash_password, verify_password
from ..schemas.token_schemas import (    
    AccessToken,
    RefreshToken,
    SignUpCompleteToken,
)
from ..schemas.otp_schemas import (
    OTPCreate,
    OTPOut,
)
from ..schemas.auth_schemas import (
    LoginRequest,
    LoginResponse,
    SignUp, 
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
    SignUpCompleteRequest,
    SignUpCompleteResponse,
    OrganizationCreate,
    UserInviteAcceptRequest,
    UserCreate
)
from ..exceptions import (
    InvalidCredentialsException,
    InvalidTokenException,
    UserAlreadyExistsException,
    UserNotActiveException, 
    UserNotFoundException,
    PasswordResetNotAllowedException,
    InvalidOTPException,
    UserBlockedException,
    UserDisabledException,
    UserNotVerifiedException,
)
from src.authorization.services import AuthorizationService

class AuthService:
    def __init__(self, 
        auth_repo: AuthRepository, 
        token_service: TokenService,
        user_service: UserService, 
        otp_service: OTPService, 
        email_service: EmailService,
        organization_service: OrganizationService,
        authorization_service: AuthorizationService,
    ) -> None:
        self.auth_repo = auth_repo
        self.token_service = token_service
        self.user_service = user_service
        self.otp_service = otp_service
        self.email_service = email_service
        self.organization_service = organization_service
        self.authorization_service = authorization_service

    async def sign_up(self, data: SignUp) -> UserOut:
        """Sign up a new user using email and password. Any extra user fields can be updated from the user service in 'users' package."""
        try:
            user = await self.user_service.get_user_by_email(data.email)
            raise UserAlreadyExistsException()
        except UserNotFoundException:
            pass
        user_create = UserCreate(
            **data.model_dump(exclude={"password", "confirm_password"}),
            password=hash_password(data.password),
            type=UserType.CLIENT, 
            status=UserStatus.PENDING, 
            role_id=None, 
            is_completed=False,
            is_super_admin=True,
        )
        user = await self.user_service.create_user(user_create)
        email_verification_otp_request = RequestEmailVerificationOTPRequest(email=data.email)
        await self.request_email_verification_otp(email_verification_otp_request)
        return user


    async def sign_up_complete(self, email: str, data: SignUpCompleteRequest) -> SignUpCompleteResponse:
        """Complete the signup process after verifying the email."""
        # if data.vat_number[10] == "1":
        #     tin_number = data.vat_number[:10]
        #     data_dict.update({"organization_unit_name": tin_number})    
        # else:
        #     data_dict.update({"organization_unit_name": data.registration_name})
        user = await self.user_service.get_user_by_email(email)
        organization_create = OrganizationCreate(**data.model_dump())
        organization, branch = await self.organization_service.create_organization_and_main_branch(organization_create)
        super_admin_role_id = await self.authorization_service.create_default_roles(organization.id)
        await self.authorization_service.create_user_permissions_after_signup(organization.id, user.id)
        await self.user_service.update_by_email(
            email, 
            {
                "is_completed": True, 
                "organization_id": organization.id,
                "branch_id": branch.id,
                "role_id": super_admin_role_id,
            }
        )
        return SignUpCompleteResponse(**organization.model_dump())
        

    async def accept_invitation(self, data: UserInviteAcceptRequest) -> UserOut:
        user = await self.get_user_from_token(data.token)
        if user.is_completed == True or user.status != UserStatus.PENDING:
            raise UserAlreadyExistsException()
        data.password = hash_password(data.password)
        data_dict = data.model_dump(exclude={"confirm_password", "token"})
        data_dict.update({
            "status": UserStatus.ACTIVE, 
            "is_completed": True
        })
        await self.user_service.update_by_email(user.email, data_dict)
        return await self.user_service.get_user_by_email(user.email)


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
            db_user: UserInDB = await self.user_service.increment_invalid_login_attempts(credentials.email)
            if db_user.invalid_login_attempts >= settings.MAXIMUM_NUMBER_OF_INVALID_LOGIN_ATTEMPTS:
                await self.user_service.update_user_status(credentials.email, UserStatus.DISABLED)
            raise InvalidCredentialsException()
        await self.user_service.reset_invalid_login_attempts(credentials.email)
        await self.user_service.update_last_login(credentials.email, datetime.utcnow())
        user = await self.user_service.get_user_by_email(db_user.email)
        return LoginResponse(user=user)


    async def get_me(self, email: str) -> UserOut:
        return await self.user_service.get_user_by_email(email)


    async def request_email_verification_otp(self, data: RequestEmailVerificationOTPRequest) -> RequestEmailVerificationOTPResponse:
        """Creates an OTP code for email verification and sends it to the email. This function will not work for blocked users."""
        user = await self.user_service.get_user_by_email(data.email)
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
        user = await self.user_service.get_user_by_email(data.email)
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


    async def verify_email_after_signup(self, data: VerifyEmailRequest) -> LoginResponse:
        """Verifies email account after signup. The function will create access and refresh token after finishing the verificaion successfully."""
        await self.verify_email_verification_otp(data)
        await self.user_service.reset_invalid_login_attempts(data.email)
        await self.user_service.update_last_login(data.email, datetime.utcnow())
        user = await self.user_service.get_user_by_email(data.email)
        return LoginResponse(user=user)
    

    async def reset_password(self, data: ResetPasswordRequest) -> ResetPasswordResponse:
        """Resets the password for a user. The user needs to have a verified OTP code that is not expired to reset his password."""
        otp: OTPOut = await self.otp_service.get_otp_by_email_and_usage(data.email, OTPUsage.PASSWORD_RESET)
        if not otp or otp.status != OTPStatus.VERIFIED or otp.email != data.email or await self.otp_service.otp_is_expired(otp.code):
            raise PasswordResetNotAllowedException()
        hashed_password = hash_password(data.password)
        user = await self.user_service.update_by_email(data.email, update_data={"password": hashed_password})
        await self.user_service.reset_invalid_login_attempts(data.email)
        await self.user_service.update_user_status(data.email, UserStatus.ACTIVE)
        return ResetPasswordResponse(email=data.email)


    async def create_access_token_and_set_cookie(self, request: Request, response: Response, user_id: int, branch_id: int, organization_id: int) -> str:
        """Creates an access token and sets it in the response cookies. Returns the access token."""
        user = await self.user_service.get_user(user_id)
        permissions = await self.authorization_service.get_user_permissions(organization_id, user.id)
        payload = AccessToken(sub=user_id, permissions=permissions, branch_id=branch_id, organization_id=organization_id)
        access_token = self.token_service.create_access_token(payload)
        self.token_service.set_access_token_cookie(request, response, access_token)
        return access_token


    async def create_refresh_token_and_set_cookie(self, request: Request, response: Response, user_id: int, branch_id: int, organization_id: int) -> str:
        """Creates a refresh token and sets it in the response cookies. Returns the refresh token."""
        payload = RefreshToken(sub=user_id, branch_id=branch_id, organization_id=organization_id)
        refresh_token = self.token_service.create_refresh_token(payload)
        self.token_service.set_refresh_token_cookie(request, response, refresh_token)
        return refresh_token


    async def create_sign_up_complete_token_and_set_cookie(self, request: Request, response: Response, user_id: int) -> str:
        """Creates a refresh token and sets it in the response cookies. Returns the refresh token."""
        payload = SignUpCompleteToken(sub=user_id)
        token = self.token_service.create_sign_up_complete_token(payload)
        self.token_service.set_sign_up_complete_token_cookie(request, response, token)
        return token


    async def create_tokens_and_set_cookies(self, request: Request, response: Response, user_id: int, branch_id: int, organization_id: int) -> tuple[str, str]:
        """Creates access and refresh tokens and sets them in the response cookies. Returns the access and refresh tokens."""
        access_token = await self.create_access_token_and_set_cookie(request, response, user_id, branch_id, organization_id)
        refresh_token = await self.create_refresh_token_and_set_cookie(request, response, user_id, branch_id, organization_id)
        return access_token, refresh_token

    
    async def refresh(self, request: Request, response: Response, refresh_token: str) -> None:
        """Refreshes an expired access token using a valid refresh token and returns the new access token."""
        token_payload: dict = self.token_service.decode_token(refresh_token)
        user_id, branch_id, organization_id = token_payload["sub"], token_payload["branch_id"], token_payload["organization_id"]
        await self.create_access_token_and_set_cookie(request, response, user_id, branch_id, organization_id)


    async def get_user_from_token(self, token: str) -> UserOut:
        """Extracts user from a valid token."""
        token_payload: dict = self.token_service.decode_token(token)
        user_id: int = token_payload["sub"]
        return await self.user_service.get_user(user_id)
