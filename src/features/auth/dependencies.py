from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from .service import AuthService, build_user_response

security = HTTPBearer()


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Dependency to get the current authenticated user from JWT token
    Use this in route parameters to protect endpoints
    
    Example:
        @router.get("/me")
        async def get_me(current_user = Depends(get_current_user)):
            return current_user
    """
    token = credentials.credentials
    
    # Verify token
    payload = AuthService.verify_token(token, token_type="access")
    user_id = payload.get("sub")
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
    # Get user from database
    user = await AuthService.get_user_by_id(user_id)
    
    return build_user_response(user)


async def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Dependency to get current user ID from JWT token
    Returns only the user ID string
    """
    token = credentials.credentials
    
    # Verify token
    payload = AuthService.verify_token(token, token_type="access")
    user_id = payload.get("sub")
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
    return user_id