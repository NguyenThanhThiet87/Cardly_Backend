from fastapi import HTTPException, status


class AuthException(HTTPException):
    """Base authentication exception"""
    pass


class InvalidCredentialsException(AuthException):
    """Raised when credentials are invalid"""
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )


class UserNotFoundExcception(AuthException):
    """Raised when user is not found"""
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )


class UserAlreadyExistsException(AuthException):
    """Raised when user already exists"""
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )


class InvalidTokenException(AuthException):
    """Raised when token is invalid"""
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )


class UnauthorizedException(AuthException):
    """Raised when user is unauthorized"""
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Unauthorized access"
        )
