from typing import Annotated
from fastapi import (
    APIRouter,
    Depends,
    Request,
    Response,
    status,
)
from src.core.enums import TokenScope
from src.users.schemas import UserInDB, UserOut
from src.core.schemas import SingleObjectResponse, SuccessfulResponse, ErrorResponse
from fastapi.security import OAuth2PasswordRequestForm
from redis.asyncio import Redis
from .services.auth_service import AuthService
from .schemas.auth_schemas import (
    UserInviteAcceptRequest,
    LoginRequest,
    LoginResponse,
    SignUp,
    SignUpCompleteRequest,
    SignUpCompleteResponse,
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
)
from .dependencies import (
    get_auth_service,
    get_redis,
)
from src.core.dependencies.auth import get_request_context, get_current_user_from_sign_up_complete_token, oauth2_scheme
from src.core.schemas.context import RequestContext
from src.docs.auth import RESPONSES, DOCSTRINGS, SUMMARIES


# ---------------------------------------------------------------------
# Router Definition
# ---------------------------------------------------------------------
router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


# ---------------------------------------------------------------------
# GET routes
# ---------------------------------------------------------------------
@router.get(
    "/me",
    response_model=SingleObjectResponse[RequestContext],
    responses=RESPONSES["get_me"],
    summary=SUMMARIES["get_me"],
    description=DOCSTRINGS["get_me"],
)
async def get_me(
    request_context: Annotated[RequestContext, Depends(get_request_context)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> SingleObjectResponse[RequestContext]:
    return SingleObjectResponse(data=request_context)


# ---------------------------------------------------------------------
# POST routes
# ---------------------------------------------------------------------
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
    data = await auth_service.sign_up(body)
    return SingleObjectResponse(data=data)


@router.post(
    "/signup/complete",
    response_model=SingleObjectResponse[SignUpCompleteResponse],
    responses=RESPONSES["sign_up_complete"],
    summary=SUMMARIES["sign_up_complete"],
    description=DOCSTRINGS["sign_up_complete"],
)
async def sign_up_complete(
    request: Request,
    response: Response,
    body: SignUpCompleteRequest,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    request_context: Annotated[RequestContext, Depends(get_current_user_from_sign_up_complete_token)],
) -> SingleObjectResponse[SignUpCompleteResponse]:
    data = await auth_service.sign_up_complete(request_context.user.email, body)
    response.delete_cookie("sign_up_complete_token")
    await auth_service.create_tokens_and_set_cookies(
        request, 
        response, 
        request_context.user.id, 
        request_context.branch.id, 
        request_context.organization.id
    )
    return SingleObjectResponse(data=data)


@router.post(
    "/invitations/accept",
    response_model=SingleObjectResponse[UserOut],
)
async def accept_invitation(
    body: UserInviteAcceptRequest,
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
    request: Request,
    response: Response,
    body: LoginRequest,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> SingleObjectResponse[LoginResponse]:
    data = await auth_service.login(body)
    #########################################
    # SET CURRENT BRANCH AS THE DEFAULT BRANCH IN THE USERS'S DATA
    #########################################
    await auth_service.create_tokens_and_set_cookies(
        request, 
        response, 
        data.user.id,
        data.user.branch_id,
        data.user.organization_id
    )
    return SingleObjectResponse(data=data)


@router.post(
    "/refresh",
    status_code=status.HTTP_204_NO_CONTENT,
    responses=RESPONSES["refresh"],
    summary=SUMMARIES["refresh"],
    description=DOCSTRINGS["refresh"],
)
async def refresh(
    request: Request,
    response: Response,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> None:
    refresh_token = request.cookies.get("refresh_token")
    await auth_service.refresh(request, response, refresh_token)


@router.post(
    "/verify-email",
    response_model=SingleObjectResponse[LoginResponse],
    responses=RESPONSES["verify_email_after_signup"],
    summary=SUMMARIES["verify_email_after_signup"],
    description=DOCSTRINGS["verify_email_after_signup"],
)
async def verify_email_after_signup(
    request: Request,
    response: Response,
    body: VerifyEmailRequest,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> SingleObjectResponse[LoginResponse]:
    data = await auth_service.verify_email_after_signup(body)
    await auth_service.create_sign_up_complete_token_and_set_cookie(request, response, data.user.id)
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


@router.post(
    "/logout",
    response_model=SuccessfulResponse,
    responses=RESPONSES["logout"],
    summary=SUMMARIES["logout"],
    description=DOCSTRINGS["logout"],
)
async def logout(
    request: Request,
    response: Response,
) -> SuccessfulResponse:
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    return SuccessfulResponse(detail="Logged out successfully")


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


@router.post(
    "/swaggerlogin",
    responses=RESPONSES["swaggerlogin"],
    summary=SUMMARIES["swaggerlogin"],
    description=DOCSTRINGS["swaggerlogin"],
)
async def swaggerlogin(
    request: Request,
    response: Response,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    login_credentials: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> dict[str, str]:
    login_data = LoginRequest(
        email=login_credentials.username,
        password=login_credentials.password,
    )
    login_response: LoginResponse = await auth_service.login(login_data)
    access_token, refresh_token = await auth_service.create_tokens_and_set_cookies(request, response, login_response.user.id)
    return {"access_token": access_token, "token_type": "bearer"}
