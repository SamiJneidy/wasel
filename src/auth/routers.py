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
    LogoutResponse,
    UserOut,
    SingleObjectResponse,
)
from .dependencies import (
    Annotated,
    Depends, 
    get_auth_service,
    get_current_user,
    get_redis,
    oauth2_scheme
)

router = APIRouter(
    prefix="/auth", 
    tags=["Authentication"],
)


@router.post(
    path="/signup",
    response_model=SingleObjectResponse[UserOut],
    responses={
        status.HTTP_200_OK: {
            "description": "The user has signed up successfully."
        },
        status.HTTP_409_CONFLICT: {
            "description": "The email has been registered before.",
            "content": {
                "application/json": {
                    "examples": {
                        "EmailAlreadyInUse": {
                            "value": {
                                "detail": "Email already in use"
                            }
                        },
                    }
                }
            }
        },
        status.HTTP_503_SERVICE_UNAVAILABLE: {
            "description": "The OTP code was not sent to the email. This may happen due to invalid email address or because of an error in the email server. You can try again later to see if the problem persists.",
            "content": {
                "application/json": {
                    "examples": {
                        "OTPCouldNotBeSent": {
                            "value": {
                                "detail": "OTP code could not be sent to the email"
                            }
                        }
                    }
                }
            }
        }
    }
)
async def signup(
    body: SignUp,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> SingleObjectResponse[UserOut]:
    """Sign up a new user.""" 
    data = await auth_service.signup(body)
    return SingleObjectResponse(data=data)

@router.post(
    path="/signup/complete",
    response_model=SingleObjectResponse[UserOut],
    responses={
        status.HTTP_200_OK: {
            "description": "Updated user successfully."
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "User was not found.",
            "content": {
                "application/json": {
                    "examples": {
                        "UserNotFound": {
                            "value": {
                                "detail": "User not found"
                            }
                        },
                    }
                }
            }
        },
    }
)
async def sign_up_complete(
    response: Response,
    body: SignUpCompleteRequest,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    current_user: Annotated[UserOut, Depends(get_current_user)],
) -> SingleObjectResponse[UserOut]:
    """Complete the sign up process after the user verifies his email."""
    data = await auth_service.sign_up_complete(current_user.email, body)
    await auth_service.set_refresh_token_cookie(data.email, response, "/api/v1/auth/refresh")
    return SingleObjectResponse(data=data)


@router.post(
    path="/login",
    response_model=LoginResponse,
    responses={
        status.HTTP_200_OK: {
            "description": "Logged in successfully."
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "User was not found.",
            "content": {
                "application/json": {
                    "examples": {
                        "UserNotFound": {
                            "value": {
                                "detail": "User not found"
                            }
                        },
                    }
                }
            }
        },
        status.HTTP_403_FORBIDDEN: {
            "description": "This error happens when the user status is not active or the user is blocked.",
            "content": {
                "application/json": {
                    "examples": {
                        "UserNotActive": {
                            "value": {
                                "detail": "Your accounts is not active. You can not perform the action."
                            }
                        },
                        "UserBlocked": {
                            "value": {
                                "detail": "Your accounts is blocked. Please contact the support to discuss the issue."
                            }
                        },
                        "UserDisabled": {
                            "value": {
                                "detail": "Your account is disabled. This usually happens due to security reasons or multiple invalid login attempts. Please reset your password and try again."
                            }
                        },
                        "UserNotVerified": {
                            "value": {
                                "detail": "Your account is not verified. Verify your account and try again."
                            }
                        },
                    }
                }
            }
        },
        status.HTTP_401_UNAUTHORIZED: {
            "description": "The login credentials are invalid.",
            "content": {
                "application/json": {
                    "examples": {
                        "InvalidCredentials": {
                            "value": {
                                "detail": "Invalid credentials"
                            }
                        },
                    }
                }
            }
        }
    }
)
async def login(
    response: Response,
    data: LoginRequest,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> LoginResponse:
    login_response: LoginResponse = await auth_service.login(data)
    await auth_service.set_refresh_token_cookie(data.email, response, "/api/v1/auth/refresh")
    return login_response

@router.get(
    path="/me",
    response_model=UserOut,
    responses={
        status.HTTP_200_OK: {
            "description": "The current user returned successfully."
        },
        status.HTTP_401_UNAUTHORIZED: {
            "description": "The current user could not be returned. This happens due to invalid or expired token.",
            "content": {
                "application/json": {
                    "examples": {
                        "InvalidToken": {
                            "value": {
                                "detail": "Invalid token"
                            }
                        }
                    }
                }
            }
        }
    }

)
async def get_me(
    current_user: Annotated[UserOut, Depends(get_current_user)],
) -> UserOut:
    """Returns the current user who is logged in."""
    return current_user


@router.post(
    path="/refresh",
    response_model=TokenRefreshResponse,
    responses={
        status.HTTP_200_OK: {
            "description": "Generated new access token and refresh token successfully."
        },
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Could not generate new access token. This happens because the refresh token is invalid.",
            "content": {
                "application/json": {
                    "InvalidToken": {
                        "value": {
                            "detail": "Invalid token"
                        }
                    }
                }
            }
        }
    }
)
async def refresh(
    request: Request,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> TokenRefreshResponse:
    """Refreshes an expired access token using a valid refresh token and sets new refresh token in HTTP-only cookie."""
    refresh_token = request.cookies.get("refresh_token")
    access_token = await auth_service.refresh(refresh_token)
    return TokenRefreshResponse(access_token=access_token)


@router.post(
    path="/verify-email", 
    response_model=LoginResponse,
    responses={
        status.HTTP_200_OK: {
            "description": "The verification has been completed successfully."
        },
        status.HTTP_401_UNAUTHORIZED: {
            "description": "The OTP code was not verified. This happens in case of invalid or expired OTP code.",
            "content": {
                "application/json": {
                    "examples": {
                        "InvalidOTP": {
                            "value": {
                                "detail": "The OTP code is invalid or has expired or has been used before"
                            }
                        },
                    }
                }
            }
        }
    }
)
async def verify_email_after_signup(
    data: VerifyEmailRequest,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> LoginResponse:
    """Verifies an email after signup and returns access and refresh tokens.""" 
    return await auth_service.verify_email_after_signup(data)


@router.post(
    path="/reset-password", 
    response_model=ResetPasswordResponse,
    responses={
        status.HTTP_200_OK: {
            "description": "The verification has been completed successfully."
        },
        status.HTTP_401_UNAUTHORIZED: {
            "description": "The OTP code was not verified. This happens in case of invalid or expired OTP code.",
            "content": {
                "application/json": {
                    "examples": {
                        "InvalidOTP": {
                            "value": {
                                "detail": "The OTP code is invalid or has expired or has been used before"
                            }
                        },
                    }
                }
            }
        }
    }
)
async def reset_password(
    data: ResetPasswordRequest,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> ResetPasswordResponse:
    """Resets the passwords after verifying a password-reset OTP code.""" 
    return await auth_service.reset_password(data)


@router.post(
    path="/logout",
    response_model=LogoutResponse,
    responses={
        status.HTTP_200_OK: {
            "description": "Logged out successfully.",
        }
    }
)
async def logout(token: str = Depends(oauth2_scheme), redis: Redis = Depends(get_redis)) -> LogoutResponse:
    await redis.setex(f"blacklist:{token}", 600, "revoked")
    return LogoutResponse(detail="Logged out successfully")


@router.post(
    path="/otp/request/email-verification", 
    response_model=RequestEmailVerificationOTPResponse,
    responses={
        status.HTTP_200_OK: {
            "description": "The OTP code has been created and sent to the email successfully."
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "User was not found.",
            "content": {
                "application/json": {
                    "examples": {
                        "UserNotFound": {
                            "value": {
                                "detail": "User not found"
                            }
                        },  
                    }
                }
            }
        },
        status.HTTP_403_FORBIDDEN: {
            "description": "This error happens when the user status is not active or the user is blocked.",
            "content": {
                "application/json": {
                    "examples": {
                        "UserBlocked": {
                            "value": {
                                "detail": "Your accounts is blocked. Please contact the support to discuss the issue."
                            }
                        },
                        "UserDisabled": {
                            "value": {
                                "detail": "our account is disabled. This usually happens due to security reasons or multiple invalid login attempts. Please reset your password and try again."
                            }
                        },
                    }
                }
            }
        },
       status.HTTP_503_SERVICE_UNAVAILABLE: {
            "description": "The OTP code was not sent to the email. This happens due to invalid email address or because of an error in the email server. Check your email and try again later.",
            "content": {
                "application/json": {
                    "examples": {
                        "OTPCouldNotBeSent": {
                            "value": {
                                "detail": "OTP code could not be sent to the email"
                            }
                        }
                    }
                }
            }
        }
    }
)
async def request_email_verification_otp(
    data: RequestEmailVerificationOTPRequest,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> RequestEmailVerificationOTPResponse:
    """Create an OTP code for password reset and send it to the user's email.""" 
    return await auth_service.request_email_verification_otp(data)


@router.post(
    path="/otp/request/password-reset", 
    response_model=RequestPasswordResetOTPResponse,
    responses={
        status.HTTP_200_OK: {
            "description": "The OTP code has been created and sent to the email successfully."
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "User was not found.",
            "content": {
                "application/json": {
                    "examples": {
                        "UserNotFound": {
                            "value": {
                                "detail": "User not found"
                            }
                        },  
                    }
                }
            }
        },
        status.HTTP_403_FORBIDDEN: {
            "description": "This error happens when the user status is not active or the user is blocked.",
            "content": {
                "application/json": {
                    "examples": {
                        "UserBlocked": {
                            "value": {
                                "detail": "Your accounts is blocked. Please contact the support to discuss the issue."
                            }
                        },
                        "UserNotVerified": {
                            "value": {
                                "detail": "Your account is not verified. Verify your account and try again."
                            }
                        },
                    }
                }
            }
        },
       status.HTTP_503_SERVICE_UNAVAILABLE: {
            "description": "The OTP code was not sent to the email. This may happen due to invalid email address or because of an error in the email server. You can try again later to see if the problem persists.",
            "content": {
                "application/json": {
                    "examples": {
                        "OTPCouldNotBeSent": {
                            "value": {
                                "detail": "OTP code could not be sent to the email"
                            }
                        }
                    }
                }
            }
        }
    }
)
async def request_password_reset_otp(
    data: RequestPasswordResetOTPRequest,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],

) -> RequestPasswordResetOTPResponse:
    """Create an OTP code for password reset and send it to the user's email.""" 
    return await auth_service.request_password_reset_otp(data)


@router.post(
    path="/otp/verify/email-verification", 
    response_model=VerifyEmailResponse,
    responses={
        status.HTTP_200_OK: {
            "description": "The verification has been completed successfully."
        },
        status.HTTP_401_UNAUTHORIZED: {
            "description": "The OTP code was not verified. This happens in case of invalid or expired OTP code.",
            "content": {
                "application/json": {
                    "examples": {
                        "InvalidOTP": {
                            "value": {
                                "detail": "The OTP code is invalid or has expired or has been used before"
                            }
                        },
                    }
                }
            }
        }
    }
)
async def verify_email_verification_otp(
    data: VerifyEmailRequest,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> VerifyEmailResponse:
    """Verify an OTP code for email verification.""" 
    return await auth_service.verify_email_verification_otp(data)


@router.post(
    path="/otp/verify/password-reset", 
    response_model=VerifyPasswordResetOTPResponse,
    responses={
        status.HTTP_200_OK: {
            "description": "The verification has been completed successfully."
        },
        status.HTTP_401_UNAUTHORIZED: {
            "description": "The OTP code was not verified. This happens in case of invalid or expired OTP code.",
            "content": {
                "application/json": {
                    "examples": {
                        "InvalidOTP": {
                            "value": {
                                "detail": "The OTP code is invalid or has expired or has been used before"
                            }
                        },
                    }
                }
            }
        }
    }
)
async def verify_password_reset_otp(
    data: VerifyPasswordResetOTPRequest,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> VerifyPasswordResetOTPResponse:
    """Verify an OTP code for password reset.""" 
    return await auth_service.verify_password_reset_otp(data)


@router.post(
    path="/swaggerlogin", 
    responses={
        status.HTTP_200_OK: {
            "description": "Logged in successfully",
        },
    },
)
async def swaggerlogin(
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    login_credentials: OAuth2PasswordRequestForm = Depends(), 
) -> dict[str, str]:
    """This is for SwaggerUI authentication for testing purposes only. Don't use this endpoint if you want to login as a frontend, use the login endpoint instead."""
    login_data = LoginRequest(email=login_credentials.username, password=login_credentials.password)
    login_response: LoginResponse = await auth_service.login(login_data)
    return {"access_token": login_response.access_token, "token_type": "bearer"}
