from fastapi import APIRouter, Request, status, Response
from fastapi.security import OAuth2PasswordRequestForm
from redis.asyncio import Redis

from .services.auth import AuthService
from .schemas import (
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
    SuccessfulResponse
)
from .dependencies import (
    Annotated,
    Depends, 
    get_auth_service,
    get_current_user,
    get_redis,
    oauth2_scheme
)

from src.docs.auth import RESPONSES, DOCSTRINGS, SUMMARIES


router = APIRouter(
    prefix="/auth", 
    tags=["Authentication"],
)


@router.post(
    path="/signup",
    response_model=SingleObjectResponse[UserOut],
    responses=RESPONSES["signup"],
    summary=SUMMARIES["signup"],
    description=DOCSTRINGS["signup"]
)
async def signup(
    body: SignUp,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> SingleObjectResponse[UserOut]:
    data = await auth_service.signup(body)
    return SingleObjectResponse(data=data)


@router.post(
    path="/signup/complete",
    response_model=SingleObjectResponse[UserOut],
    responses=RESPONSES["sign_up_complete"],
    summary=SUMMARIES["sign_up_complete"],
    description=DOCSTRINGS["sign_up_complete"]
)
async def sign_up_complete(
    response: Response,
    body: SignUpCompleteRequest,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    current_user: Annotated[UserOut, Depends(get_current_user)],
) -> SingleObjectResponse[UserOut]:
    data = await auth_service.sign_up_complete(current_user.email, body)
    await auth_service.set_refresh_token_cookie(data.email, response, "/api/v1/auth/refresh")
    return SingleObjectResponse(data=data)


@router.post(
    path="/login",
    response_model=SingleObjectResponse[LoginResponse],
    responses=RESPONSES["login"],
    summary=SUMMARIES["login"],
    description=DOCSTRINGS["login"]
)
async def login(
    response: Response,
    body: LoginRequest,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> SingleObjectResponse[LoginResponse]:
    data = await auth_service.login(body)
    await auth_service.set_refresh_token_cookie(body.email, response, "/api/v1/auth/refresh")
    return SingleObjectResponse(data=data)


@router.get(
    path="/me",
    response_model=SingleObjectResponse[UserOut],
    responses=RESPONSES["get_me"],
    summary=SUMMARIES["get_me"],
    description=DOCSTRINGS["get_me"]
)
async def get_me(
    current_user: Annotated[UserOut, Depends(get_current_user)],
) -> SingleObjectResponse[UserOut]:
    return SingleObjectResponse(data=current_user)


@router.post(
    path="/refresh",
    response_model=SingleObjectResponse[TokenRefreshResponse],
    responses=RESPONSES["refresh"],
    summary=SUMMARIES["refresh"],
    description=DOCSTRINGS["refresh"]
)
async def refresh(
    request: Request,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> SingleObjectResponse[TokenRefreshResponse]:
    refresh_token = request.cookies.get("refresh_token")
    access_token = await auth_service.refresh(refresh_token)
    return SingleObjectResponse(data=TokenRefreshResponse(access_token=access_token))


@router.post(
    path="/verify-email", 
    response_model=SingleObjectResponse[LoginResponse],
    responses=RESPONSES["verify_email_after_signup"],
    summary=SUMMARIES["verify_email_after_signup"],
    description=DOCSTRINGS["verify_email_after_signup"]
)
async def verify_email_after_signup(
    body: VerifyEmailRequest,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> SingleObjectResponse[LoginResponse]:
    data = await auth_service.verify_email_after_signup(body)
    return SingleObjectResponse(data=data)


@router.post(
    path="/reset-password", 
    response_model=SingleObjectResponse[ResetPasswordResponse],
    responses=RESPONSES["reset_password"],
    summary=SUMMARIES["reset_password"],
    description=DOCSTRINGS["reset_password"]
)
async def reset_password(
    body: ResetPasswordRequest,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> SingleObjectResponse[ResetPasswordResponse]:
    data = await auth_service.reset_password(body)
    return SingleObjectResponse(data=data)

@router.post(
    path="/logout",
    response_model=SuccessfulResponse,
    responses=RESPONSES["logout"],
    summary=SUMMARIES["logout"],
    description=DOCSTRINGS["logout"]
)
async def logout(
    token: str = Depends(oauth2_scheme), 
    redis: Redis = Depends(get_redis)
) -> SuccessfulResponse:
    await redis.setex(f"blacklist:{token}", 600, "revoked")
    return SuccessfulResponse(detail="Logged out successfully")


@router.post(
    path="/otp/request/email-verification", 
    response_model=SingleObjectResponse[RequestEmailVerificationOTPResponse],
    responses=RESPONSES["request_email_verification_otp"],
    summary=SUMMARIES["request_email_verification_otp"],
    description=DOCSTRINGS["request_email_verification_otp"]
)
async def request_email_verification_otp(
    body: RequestEmailVerificationOTPRequest,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> SingleObjectResponse[RequestEmailVerificationOTPResponse]:
    data = await auth_service.request_email_verification_otp(body)
    return SingleObjectResponse(data=data)

@router.post(
    path="/otp/request/password-reset", 
    response_model=SingleObjectResponse[RequestPasswordResetOTPResponse],
    responses=RESPONSES["request_password_reset_otp"],
    summary=SUMMARIES["request_password_reset_otp"],
    description=DOCSTRINGS["request_password_reset_otp"]
)
async def request_password_reset_otp(
    body: RequestPasswordResetOTPRequest,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> SingleObjectResponse[RequestPasswordResetOTPResponse]:
    data = await auth_service.request_password_reset_otp(body)
    return SingleObjectResponse(data=data)


@router.post(
    path="/otp/verify/email-verification", 
    response_model=SingleObjectResponse[VerifyEmailResponse],
    responses=RESPONSES["verify_email_verification_otp"],
    summary=SUMMARIES["verify_email_verification_otp"],
    description=DOCSTRINGS["verify_email_verification_otp"]
)
async def verify_email_verification_otp(
    body: VerifyEmailRequest,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> SingleObjectResponse[VerifyEmailResponse]:
    data = await auth_service.verify_email_verification_otp(body)
    return SingleObjectResponse(data=data)

@router.post(
    path="/otp/verify/password-reset", 
    response_model=SingleObjectResponse[VerifyPasswordResetOTPResponse],
    responses=RESPONSES["verify_password_reset_otp"],
    summary=SUMMARIES["verify_password_reset_otp"],
    description=DOCSTRINGS["verify_password_reset_otp"]
)
async def verify_password_reset_otp(
    body: VerifyPasswordResetOTPRequest,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> SingleObjectResponse[VerifyPasswordResetOTPResponse]:
    data = await auth_service.verify_password_reset_otp(body)
    return SingleObjectResponse(data=data)

@router.post(
    path="/swaggerlogin", 
    responses=RESPONSES["swaggerlogin"],
    summary=SUMMARIES["swaggerlogin"],
    description=DOCSTRINGS["swaggerlogin"]
)
async def swaggerlogin(
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    login_credentials: OAuth2PasswordRequestForm = Depends(), 
) -> dict[str, str]:
    login_data = LoginRequest(email=login_credentials.username, password=login_credentials.password)
    login_response: LoginResponse = await auth_service.login(login_data)
    return {"access_token": login_response.access_token, "token_type": "bearer"}
