from fastapi import APIRouter, status, Depends
from .schemas import RegisterRequest, LoginRequest, AuthResponse, TokenResponse, RefreshTokenRequest, UserResponse
from .service import AuthService, build_user_response
from .dependencies import get_current_user

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
    # Register user
    user_doc = await AuthService.register(user_data)
    
    # Create tokens
    access_token, expires_in = AuthService.create_access_token(str(user_doc["_id"]))
    refresh_token = AuthService.create_refresh_token(str(user_doc["_id"]))
    
    # Build response
    user_response = build_user_response(user_doc)
    
    return AuthResponse(
        user=user_response,
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=expires_in
    )


@router.post("/login", response_model=AuthResponse)
async def login(credentials: LoginRequest):
    """
    Login with email or username and password
    
    Returns access token and refresh token
    """
    # Authenticate user
    user = await AuthService.login(credentials.identifier, credentials.password)
    
    # Create tokens
    access_token, expires_in = AuthService.create_access_token(str(user["_id"]))
    refresh_token = AuthService.create_refresh_token(str(user["_id"]))
    
    # Build response
    user_response = build_user_response(user)
    
    return AuthResponse(
        user=user_response,
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=expires_in
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(request: RefreshTokenRequest):
    """
    Refresh access token using refresh token
    
    Returns new access token
    """
    # Verify refresh token
    payload = AuthService.verify_token(request.refresh_token, token_type="refresh")
    user_id = payload.get("sub")
    
    # Create new access token
    access_token, expires_in = AuthService.create_access_token(user_id)
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=expires_in
    )


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
    
    Note: Token should be invalidated on client side
    Server-side: Consider implementing token blacklist for production
    """
    return {"message": "Logged out successfully"}
