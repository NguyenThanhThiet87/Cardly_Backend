from fastapi import APIRouter, Depends, status

from .constants import PASSWORD_RESET_EMAIL_SENT, PASSWORD_RESET_SUCCESS
from .dependencies import get_current_user
from .schemas import (
    AuthResponse,
    ForgotPasswordRequest,
    ForgotPasswordResponse,
    LoginRequest,
    MessageResponse,
    RefreshTokenRequest,
    RegisterRequest,
    ResetPasswordRequest,
    TokenResponse,
    UserResponse,
)
from .service import AuthService, build_user_response

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: RegisterRequest):
    """
    Register a new user

    - **email**: User email (must be unique)
    - **password**: 8-16 characters, including letters, numbers, special characters, and one uppercase letter
    - **full_name**: Optional user full name
    - **username**: Optional username
    """
    user_doc = await AuthService.register(user_data)

    access_token, expires_in = AuthService.create_access_token(str(user_doc["_id"]))
    refresh_token = AuthService.create_refresh_token(str(user_doc["_id"]))
    user_response = build_user_response(user_doc)

    return AuthResponse(
        user=user_response,
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=expires_in,
    )


@router.post("/login", response_model=AuthResponse)
async def login(credentials: LoginRequest):
    """
    Login with email or username and password

    Returns access token and refresh token
    """
    user = await AuthService.login(credentials.identifier, credentials.password)

    access_token, expires_in = AuthService.create_access_token(str(user["_id"]))
    refresh_token = AuthService.create_refresh_token(str(user["_id"]))
    user_response = build_user_response(user)

    return AuthResponse(
        user=user_response,
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=expires_in,
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(request: RefreshTokenRequest):
    """
    Refresh access token using refresh token

    Returns new access token
    """
    payload = AuthService.verify_token(request.refresh_token, token_type="refresh")
    user_id = payload.get("sub")

    access_token, expires_in = AuthService.create_access_token(user_id)

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=expires_in,
    )


@router.post("/forgot-password", response_model=ForgotPasswordResponse)
async def forgot_password(request: ForgotPasswordRequest):
    """
    Send a password reset link to the user's email.

    The reset link should open the frontend reset password page. The frontend
    then calls POST /api/auth/reset-password with the token and new password.
    """
    await AuthService.forgot_password(request.email)

    return ForgotPasswordResponse(message=PASSWORD_RESET_EMAIL_SENT)


@router.post("/reset-password", response_model=MessageResponse)
async def reset_password(request: ResetPasswordRequest):
    """
    Reset password using a valid reset token.

    This API is called by the frontend reset password page.
    """
    await AuthService.reset_password(request.token, request.new_password)

    return MessageResponse(message=PASSWORD_RESET_SUCCESS)


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: UserResponse = Depends(get_current_user)):
    """
    Get current authenticated user profile

    Requires: Valid JWT access token
    """
    return current_user


@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(current_user: UserResponse = Depends(get_current_user)):
    """
    Logout current user

    Note: Token should be invalidated on client side.
    """
    return {"message": "Logged out successfully"}
