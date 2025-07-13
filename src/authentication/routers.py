from fastapi import APIRouter, status, Response
from fastapi.security import OAuth2PasswordRequestForm
from redis.asyncio import Redis

from .services import OTPService, AuthenticationService
from src.core.enums import OTPUsage
from src.core.config import settings
from .schemas import (
    SignUp,
    SignUpResponse,
    Login,
    LoginResponse,
    LogoutResponse,
    OTPOut, 
    OTPVerificationRequest, 
    OTPVerificationResponse,
    PasswordResetResponse, 
    PasswordResetOTPRequest,
    PasswordResetOTPResponse,
    PasswordResetRequest,
    TokenRefreshRequest,
    TokenResponse,
    UserOut,
    EmailVerificationOTPRequest,
    EmailVerificationOTPResponse,
)
from .dependencies import (
    Annotated,
    Depends, 
    get_authentication_service,
    get_current_user,
    get_otp_service,
    get_redis,
    oauth2_scheme
)

router = APIRouter(
    prefix="/auth", 
    tags=["Authentication"],
)


@router.post(
    path="/signup",
    response_model=SignUpResponse,
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
    data: SignUp,
    auth_service: Annotated[AuthenticationService, Depends(get_authentication_service)],
) -> SignUpResponse:
    """Sign up a new user.""" 
    return await auth_service.signup(data)


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
    data: Login,
    auth_service: Annotated[AuthenticationService, Depends(get_authentication_service)],
) -> LoginResponse:
    login_response: LoginResponse = await auth_service.login(data)
    await auth_service.set_refresh_token_cookie(response, login_response.refresh_token, "/api/v1/auth/refresh")
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
    response_model=TokenResponse,
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
    token_refresh_request: TokenRefreshRequest,
    response: Response,
    auth_service: Annotated[AuthenticationService, Depends(get_authentication_service)],
) -> TokenResponse:
    """Refresh an expired access token using a valid refresh token and sets new refresh token in HTTP-only cookie."""
    token_response = await auth_service.refresh(token_refresh_request)
    await auth_service.set_refresh_token_cookie(response, token_response.refresh_token, "/api/v1/auth/refresh")
    return token_response

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
    path="/otp/generate/email-verification", 
    response_model=EmailVerificationOTPResponse,
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
async def request_email_verification(
    data: EmailVerificationOTPRequest,
    auth_service: Annotated[AuthenticationService, Depends(get_authentication_service)],

) -> EmailVerificationOTPResponse:
    """Create an OTP code for password reset and send it to the user's email.""" 
    return await auth_service.request_email_verification(data)


@router.post(
    path="/otp/generate/password-reset", 
    response_model=PasswordResetOTPResponse,
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
async def request_password_reset(
    data: PasswordResetOTPRequest,
    auth_service: Annotated[AuthenticationService, Depends(get_authentication_service)],

) -> PasswordResetOTPResponse:
    """Create an OTP code for password reset and send it to the user's email.""" 
    return await auth_service.request_password_reset(data)


@router.post(
    path="/otp/verify", 
    response_model=OTPVerificationResponse,
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
async def verify_otp(
    data: OTPVerificationRequest,
    otp_service: Annotated[OTPService, Depends(get_otp_service)],
) -> OTPVerificationResponse:
    """Verify an OTP code for email verification, password reset, ...etc. The user status will be changed to 'ACTIVE' after verifying except if his status was 'BLOCKED'.""" 
    response: OTPVerificationResponse = await otp_service.verify_otp(data)
    return response


@router.post(
    path="/reset-password", 
    response_model=PasswordResetResponse,
    responses={
        status.HTTP_200_OK: {
            "description": "The password has been reset successfully."
        },
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Could not reset the password. Request a new OTP code and try again.",
            "content": {
                "application/json": {
                    "examples": {
                        "PasswordResetNotAllowed": {
                            "value": {
                                "detail": "Password reset not allowed. Please request a new OTP code and try again."
                            }
                        }
                    }
                }
            }
        },
    }
)
async def reset_password(
    data: PasswordResetRequest,
    auth_service: Annotated[AuthenticationService, Depends(get_authentication_service)],
) -> PasswordResetResponse:
    """Reset the password of the user. Note that the user has to verify the OTP code in order to reset his password.""" 
    return await auth_service.reset_password(data)


# @router.delete(
#     path="/",
#     status_code=status.HTTP_204_NO_CONTENT
# )
# async def delete_user(
#     email: str,
#     user_service: Annotated[UserService, Depends(get_user_service)]
# ) -> None:
#     """Deletes a user by email. This endpoint is used only during the development."""
#     await user_service.delete_user(email)


@router.post(
    path="/swaggerlogin", 
    responses={
        status.HTTP_200_OK: {
            "description": "Logged in successfully",
        },
    },
)
async def swaggerlogin(
    auth_service: Annotated[AuthenticationService, Depends(get_authentication_service)],
    response: Response,
    login_credentials: OAuth2PasswordRequestForm = Depends(), 
) -> dict[str, str]:
    """This is for SwaggerUI authentication for testing purposes only. Don't use this endpoint if you want to login as a frontend, use the login endpoint instead."""
    login_data = Login(email=login_credentials.username, password=login_credentials.password)
    login_response: LoginResponse = await auth_service.login(login_data)
    return {"access_token": login_response.access_token, "token_type": "bearer"}
