from fastapi import status
from src.core.schemas import ErrorResponse

RESPONSES = {
    "signup": {
        status.HTTP_200_OK: {
            "description": "User registered successfully and OTP sent for email verification."
        },
        status.HTTP_409_CONFLICT: {
            "description": "The email is already associated with an existing account.",
            "model": ErrorResponse,
        },
        status.HTTP_503_SERVICE_UNAVAILABLE: {
            "description": "The OTP could not be delivered due to an invalid email address or a temporary email service failure.",
            "model": ErrorResponse,
        },
    },

    "sign_up_complete": {
        status.HTTP_200_OK: {
            "description": "The user profile was updated and signup process completed."
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "No user account was found for the current session.",
            "model": ErrorResponse,
        },
    },

    "login": {
        status.HTTP_200_OK: {"description": "Login successful. Access and refresh tokens issued."},
        status.HTTP_404_NOT_FOUND: {
            "description": "No user exists with the provided email address.",
            "model": ErrorResponse,
        },
        status.HTTP_403_FORBIDDEN: {
            "description": "The account is inactive, blocked, disabled, or has not yet been verified.",
            "model": ErrorResponse,
        },
        status.HTTP_401_UNAUTHORIZED: {
            "description": "The provided email or password is incorrect.",
            "model": ErrorResponse,
        },
    },

    "get_me": {
        status.HTTP_200_OK: {"description": "Authenticated user details retrieved successfully."},
        status.HTTP_401_UNAUTHORIZED: {
            "description": "The request does not include a valid access token, or the token has expired.",
            "model": ErrorResponse,
        },
    },

    "refresh": {
        status.HTTP_200_OK: {
            "description": "A new access token and refresh token pair were generated successfully."
        },
        status.HTTP_401_UNAUTHORIZED: {
            "description": "The refresh token is invalid, expired, or missing.",
            "model": ErrorResponse,
        },
    },

    "verify_email_after_signup": {
        status.HTTP_200_OK: {
            "description": "Email address verified successfully. Access and refresh tokens issued."
        },
        status.HTTP_401_UNAUTHORIZED: {
            "description": "The provided OTP is invalid, expired, or already used.",
            "model": ErrorResponse,
        },
    },

    "reset_password": {
        status.HTTP_200_OK: {
            "description": "Password reset successfully. The new password is now active."
        },
        status.HTTP_401_UNAUTHORIZED: {
            "description": "The provided OTP is invalid, expired, or already used.",
            "model": ErrorResponse,
        },
    },

    "logout": {
        status.HTTP_200_OK: {
            "description": "User logged out successfully. The access token has been revoked."
        },
    },

    "request_email_verification_otp": {
        status.HTTP_200_OK: {
            "description": "A new OTP was generated and sent to the user’s email address."
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "No user exists with the given email address.",
            "model": ErrorResponse,
        },
        status.HTTP_403_FORBIDDEN: {
            "description": "The user account is inactive or blocked. OTP request denied.",
            "model": ErrorResponse,
        },
        status.HTTP_503_SERVICE_UNAVAILABLE: {
            "description": "OTP could not be delivered due to an invalid email address or a temporary email service failure.",
            "model": ErrorResponse,
        },
    },

    "request_password_reset_otp": {
        status.HTTP_200_OK: {
            "description": "A new password reset OTP was generated and sent to the user’s email."
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "No user exists with the given email address.",
            "model": ErrorResponse,
        },
        status.HTTP_403_FORBIDDEN: {
            "description": "The user account is inactive, blocked, or not yet verified.",
            "model": ErrorResponse,
        },
        status.HTTP_503_SERVICE_UNAVAILABLE: {
            "description": "OTP could not be delivered due to an invalid email address or a temporary email service failure.",
            "model": ErrorResponse,
        },
    },

    "verify_email_verification_otp": {
        status.HTTP_200_OK: {
            "description": "The provided email verification OTP is valid and has been accepted."
        },
        status.HTTP_401_UNAUTHORIZED: {
            "description": "The OTP is invalid, expired, or has already been used.",
            "model": ErrorResponse,
        },
    },

    "verify_password_reset_otp": {
        status.HTTP_200_OK: {
            "description": "The provided password reset OTP is valid and has been accepted."
        },
        status.HTTP_401_UNAUTHORIZED: {
            "description": "The OTP is invalid, expired, or has already been used.",
            "model": ErrorResponse,
        },
    },

    "swaggerlogin": {
        status.HTTP_200_OK: {
            "description": "Swagger-only login successful. Returns a bearer token for testing."
        },
    },
}
