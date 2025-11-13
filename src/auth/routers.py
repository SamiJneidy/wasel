from fastapi import APIRouter, Query, Request, Response, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from redis.asyncio import Redis

from .services.auth_service import AuthService
from .schemas import (
    InvitationAcceptRequest,
    InviteUserRequest,
    LoginRequest,
    LoginResponse,
    SignUp,
    SignUpCompleteRequest,
    SignUpCompleteResponse,
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
    TokenRefreshResponse,
    TokenResponse,
    UserOut,
    SingleObjectResponse,
    SuccessfulResponse,
)

from .dependencies import (
    Annotated,
    get_auth_service,
    get_current_user,
    get_redis,
    oauth2_scheme,
)

from src.docs.auth import RESPONSES, DOCSTRINGS, SUMMARIES


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)

# -----------------------------------------------------------------------------
# Sign-up and Login Routes
# -----------------------------------------------------------------------------

@router.post(
    "/signup",
    response_model=SingleObjectResponse[UserOut],
    responses=RESPONSES["signup"],
    summary=SUMMARIES["signup"],
    description=DOCSTRINGS["signup"],
)
async def signup(
    body: SignUp,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> SingleObjectResponse[UserOut]:
    data = await auth_service.signup(body)
    return SingleObjectResponse(data=data)


@router.post(
    "/signup/complete",
    response_model=SingleObjectResponse[SignUpCompleteResponse],
    responses=RESPONSES["sign_up_complete"],
    summary=SUMMARIES["sign_up_complete"],
    description=DOCSTRINGS["sign_up_complete"],
)
async def sign_up_complete(
    response: Response,
    body: SignUpCompleteRequest,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    current_user_email: Annotated[UserOut, Depends(get_current_user)],
) -> SingleObjectResponse[SignUpCompleteResponse]:
    data = await auth_service.sign_up_complete(current_user_email, body)
    # await auth_service.set_token_cookies(current_user_email, response, "/api/v1/auth/refresh")
    return SingleObjectResponse(data=data)


@router.post(
    "/invitations/invite",
    response_model=SingleObjectResponse[UserOut],
    # responses=RESPONSES["sign_up_complete"],
    # summary=SUMMARIES["sign_up_complete"],
    # description=DOCSTRINGS["sign_up_complete"],
)
async def invite_user(
    request: Request,
    body: InviteUserRequest,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    current_user_email: Annotated[UserOut, Depends(get_current_user)],
) -> SingleObjectResponse[UserOut]:
    data = await auth_service.invite_user(current_user_email, request.base_url, body)
    return SingleObjectResponse(data=data)



@router.post(
    "/invitations/resend",
    response_model=SingleObjectResponse[UserOut],
    # responses=RESPONSES["sign_up_complete"],
    # summary=SUMMARIES["sign_up_complete"],
    # description=DOCSTRINGS["sign_up_complete"],
)
async def resend_invitation(
    request: Request,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    current_user_email: Annotated[UserOut, Depends(get_current_user)],
    email: str = Query(description="Email of the user to send invitation to."),
) -> SingleObjectResponse[UserOut]:
    data = await auth_service.send_invitation(email, request.base_url)
    return SingleObjectResponse(data=data)


@router.post(
    "/invitations/accept",
    response_model=SingleObjectResponse[UserOut],
    # responses=RESPONSES["sign_up_complete"],
    # summary=SUMMARIES["sign_up_complete"],
    # description=DOCSTRINGS["sign_up_complete"],
)
async def accept_invitation(
    body: InvitationAcceptRequest,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> SingleObjectResponse[UserOut]:
    data = await auth_service.accept_invitation(body)
    return SingleObjectResponse(data=data)


@router.post(
    "/login",
    response_model=SingleObjectResponse[LoginResponse],
    responses=RESPONSES["login"],
    summary=SUMMARIES["login"],
    description=DOCSTRINGS["login"],
)
async def login(
    response: Response,
    body: LoginRequest,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> SingleObjectResponse[LoginResponse]:
    data = await auth_service.login(body)
    auth_service.create_tokens_and_set_cookies(response, body.email, "/", "/api/v1/auth/refresh")
    return SingleObjectResponse(data=data)


@router.get(
    "/me",
    response_model=SingleObjectResponse[UserOut],
    responses=RESPONSES["get_me"],
    summary=SUMMARIES["get_me"],
    description=DOCSTRINGS["get_me"],
)
async def get_me(
    current_user: Annotated[UserOut, Depends(get_current_user)],
) -> SingleObjectResponse[UserOut]:
    return SingleObjectResponse(data=current_user)


@router.post(
    "/refresh",
    status_code=status.HTTP_204_NO_CONTENT,
    response_model=None,
    responses=RESPONSES["refresh"],
    summary=SUMMARIES["refresh"],
    description=DOCSTRINGS["refresh"],
)
async def refresh(
    response: Response,
    request: Request,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> None:
    refresh_token = request.cookies.get("refresh_token")
    auth_service.refresh(response, refresh_token)


# -----------------------------------------------------------------------------
# Email Verification & Password Reset
# -----------------------------------------------------------------------------

@router.post(
    "/verify-email",
    response_model=SingleObjectResponse[LoginResponse],
    responses=RESPONSES["verify_email_after_signup"],
    summary=SUMMARIES["verify_email_after_signup"],
    description=DOCSTRINGS["verify_email_after_signup"],
)
async def verify_email_after_signup(
    body: VerifyEmailRequest,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> SingleObjectResponse[LoginResponse]:
    data = await auth_service.verify_email_after_signup(body)
    return SingleObjectResponse(data=data)


@router.post(
    "/reset-password",
    response_model=SingleObjectResponse[ResetPasswordResponse],
    responses=RESPONSES["reset_password"],
    summary=SUMMARIES["reset_password"],
    description=DOCSTRINGS["reset_password"],
)
async def reset_password(
    body: ResetPasswordRequest,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> SingleObjectResponse[ResetPasswordResponse]:
    data = await auth_service.reset_password(body)
    return SingleObjectResponse(data=data)


# -----------------------------------------------------------------------------
# Logout
# -----------------------------------------------------------------------------

@router.post(
    "/logout",
    response_model=SuccessfulResponse,
    responses=RESPONSES["logout"],
    summary=SUMMARIES["logout"],
    description=DOCSTRINGS["logout"],
)
async def logout(
    token: str = Depends(oauth2_scheme),
    redis: Redis = Depends(get_redis),
) -> SuccessfulResponse:
    await redis.setex(f"blacklist:{token}", 600, "revoked")
    return SuccessfulResponse(detail="Logged out successfully")


# -----------------------------------------------------------------------------
# OTP Endpoints
# -----------------------------------------------------------------------------

@router.post(
    "/otp/request/email-verification",
    response_model=SingleObjectResponse[RequestEmailVerificationOTPResponse],
    responses=RESPONSES["request_email_verification_otp"],
    summary=SUMMARIES["request_email_verification_otp"],
    description=DOCSTRINGS["request_email_verification_otp"],
)
async def request_email_verification_otp(
    body: RequestEmailVerificationOTPRequest,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> SingleObjectResponse[RequestEmailVerificationOTPResponse]:
    data = await auth_service.request_email_verification_otp(body)
    return SingleObjectResponse(data=data)


@router.post(
    "/otp/request/password-reset",
    response_model=SingleObjectResponse[RequestPasswordResetOTPResponse],
    responses=RESPONSES["request_password_reset_otp"],
    summary=SUMMARIES["request_password_reset_otp"],
    description=DOCSTRINGS["request_password_reset_otp"],
)
async def request_password_reset_otp(
    body: RequestPasswordResetOTPRequest,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> SingleObjectResponse[RequestPasswordResetOTPResponse]:
    data = await auth_service.request_password_reset_otp(body)
    return SingleObjectResponse(data=data)


@router.post(
    "/otp/verify/email-verification",
    response_model=SingleObjectResponse[VerifyEmailResponse],
    responses=RESPONSES["verify_email_verification_otp"],
    summary=SUMMARIES["verify_email_verification_otp"],
    description=DOCSTRINGS["verify_email_verification_otp"],
)
async def verify_email_verification_otp(
    body: VerifyEmailRequest,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> SingleObjectResponse[VerifyEmailResponse]:
    data = await auth_service.verify_email_verification_otp(body)
    return SingleObjectResponse(data=data)


@router.post(
    "/otp/verify/password-reset",
    response_model=SingleObjectResponse[VerifyPasswordResetOTPResponse],
    responses=RESPONSES["verify_password_reset_otp"],
    summary=SUMMARIES["verify_password_reset_otp"],
    description=DOCSTRINGS["verify_password_reset_otp"],
)
async def verify_password_reset_otp(
    body: VerifyPasswordResetOTPRequest,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> SingleObjectResponse[VerifyPasswordResetOTPResponse]:
    data = await auth_service.verify_password_reset_otp(body)
    return SingleObjectResponse(data=data)


# -----------------------------------------------------------------------------
# Swagger Login (for documentation)
# -----------------------------------------------------------------------------

@router.post(
    "/swaggerlogin",
    responses=RESPONSES["swaggerlogin"],
    summary=SUMMARIES["swaggerlogin"],
    description=DOCSTRINGS["swaggerlogin"],
)
async def swaggerlogin(
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    login_credentials: OAuth2PasswordRequestForm = Depends(),
) -> dict[str, str]:
    from .schemas import TokenPayload
    login_data = LoginRequest(email=login_credentials.username,password=login_credentials.password,)
    login_response: LoginResponse = auth_service.login(login_data)
    access_token = auth_service.create_access_token(TokenPayload(sub=login_credentials.username))
    return {
        "access_token": access_token,
        "token_type": "bearer",
    }
