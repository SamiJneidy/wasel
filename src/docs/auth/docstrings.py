DOCSTRINGS = {
    "signup": """Register a new user in the system. 
    The user provides basic registration details (such as email and password). 
    An OTP code is sent to their email for verification. 
    If successful, a new user account is created in pending verification state.""",

    "sign_up_complete": """Complete the sign-up process after the user verifies their email. 
    This step updates additional user details and finalizes account activation. 
    A refresh token is set in a secure HTTP-only cookie.""",

    "login": """Authenticate a user using their email and password. 
    If successful, returns an access token and sets a refresh token in a secure cookie. 
    Access may be denied if the account is inactive, blocked, disabled, or not verified.""",

    "get_me": """Retrieve details of the currently authenticated user. 
    Requires a valid access token. 
    Returns profile information of the logged-in user.""",

    "refresh": """Generate a new access token using a valid refresh token. 
    A new refresh token is also issued and stored in an HTTP-only cookie. 
    Used when the current access token has expired.""",

    "verify_email_after_signup": """Verify the user's email address after signup using an OTP code. 
    Once verified, the system issues access and refresh tokens to complete the authentication process.""",

    "reset_password": """Reset the user's password after validating a password-reset OTP. 
    This allows users to regain access to their account if they forgot their password.""",

    "logout": """Logout the current user by revoking their access token. 
    The token is blacklisted for a limited time, preventing further use.""",

    "request_email_verification_otp": """Generate and send an OTP code to the user's email for email verification. 
    Used during registration when a user needs to confirm their email address.""",

    "request_password_reset_otp": """Generate and send an OTP code to the user's email for password reset. 
    Allows the user to reset their password if they forgot it or suspect compromise.""",

    "verify_email_verification_otp": """Validate an OTP code provided for email verification. 
    Ensures that the email address belongs to the user and completes the verification process.""",

    "verify_password_reset_otp": """Validate an OTP code provided for password reset. 
    If valid, the user may proceed to reset their password.""",

    "swaggerlogin": """Login endpoint intended for Swagger UI testing only. 
    Accepts form-data credentials and returns an access token. 
    Should not be used in production applications (use the regular login endpoint instead).""",
}
