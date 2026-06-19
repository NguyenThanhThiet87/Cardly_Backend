from datetime import datetime, timezone, timedelta
from typing import Optional
import hashlib
import secrets
import bcrypt
import jwt
from bson import ObjectId
from fastapi import HTTPException, status
from starlette.concurrency import run_in_threadpool
from ...core.database import get_db
from .models import UserDocument, TokenPayload
from .schemas import RegisterRequest, UserResponse
from .config import (
    SECRET_KEY,
    ALGORITHM,
    ACCESS_TOKEN_EXPIRE,
    REFRESH_TOKEN_EXPIRE,
    RESET_PASSWORD_TOKEN_EXPIRE,
    RESET_PASSWORD_TOKEN_EXPIRE_MINUTES,
    RESET_PASSWORD_URL,
)
from .constants import AUTH_COLLECTION, USER_NOT_FOUND, INVALID_CREDENTIALS, USER_ALREADY_EXISTS
from .email import send_password_reset_email


class AuthService:
    """Authentication service for handling user registration, login, and token operations"""

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password with bcrypt"""
        salt = bcrypt.gensalt(rounds=12)
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

    @staticmethod
    def hash_reset_token(token: str) -> str:
        """Hash a password reset token before storing it"""
        return hashlib.sha256(token.encode("utf-8")).hexdigest()

    @staticmethod
    def create_access_token(user_id: str, expires_delta: Optional[timedelta] = None) -> tuple[str, int]:
        """Create a JWT access token"""
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + ACCESS_TOKEN_EXPIRE

        payload = {
            "sub": user_id,
            "exp": expire,
            "iat": datetime.now(timezone.utc),
            "type": "access"
        }
        encoded_jwt = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
        expires_in = int(expires_delta.total_seconds()) if expires_delta else int(ACCESS_TOKEN_EXPIRE.total_seconds())
        return encoded_jwt, expires_in

    @staticmethod
    def create_refresh_token(user_id: str) -> str:
        """Create a JWT refresh token"""
        expire = datetime.now(timezone.utc) + REFRESH_TOKEN_EXPIRE
        payload = {
            "sub": user_id,
            "exp": expire,
            "iat": datetime.now(timezone.utc),
            "type": "refresh"
        }
        encoded_jwt = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    @staticmethod
    def verify_token(token: str, token_type: str = "access") -> dict:
        """Verify a JWT token and return the payload"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            if payload.get("type") != token_type:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token type"
                )
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )

    @staticmethod
    async def register(user_data: RegisterRequest) -> dict:
        """Register a new user"""
        db = await get_db()
        
        # Check if user already exists
        existing_user = await db[AUTH_COLLECTION].find_one({"email": user_data.email})
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=USER_ALREADY_EXISTS
            )

        # Create new user
        user_doc = {
            "email": user_data.email,
            "hashed_password": AuthService.hash_password(user_data.password),
            "full_name": user_data.full_name,
            "username": user_data.username,
            "is_active": True,
            "created_at": datetime.now(timezone.utc),
        }

        result = await db[AUTH_COLLECTION].insert_one(user_doc)
        user_doc["_id"] = result.inserted_id

        return user_doc

    @staticmethod
    async def login(identifier: str, password: str) -> dict:
        """Authenticate user and return user document"""
        db = await get_db()

        # Find user by email or username
        user = await db[AUTH_COLLECTION].find_one(
            {"$or": [{"email": identifier}, {"username": identifier}]}
        )
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=INVALID_CREDENTIALS
            )

        # Verify password
        if not AuthService.verify_password(password, user["hashed_password"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=INVALID_CREDENTIALS
            )

        # Check if user is active
        if not user.get("is_active", True):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive"
            )

        return user

    @staticmethod
    async def forgot_password(email: str) -> None:
        """Generate a one-time password reset token and email it to the user"""
        db = await get_db()
        user = await db[AUTH_COLLECTION].find_one({"email": email})

        if not user:
            return None

        reset_token = secrets.token_urlsafe(32)
        expires_at = datetime.now(timezone.utc) + RESET_PASSWORD_TOKEN_EXPIRE
        reset_link = f"{RESET_PASSWORD_URL}?token={reset_token}"

        await db[AUTH_COLLECTION].update_one(
            {"_id": user["_id"]},
            {
                "$set": {
                    "reset_password_token_hash": AuthService.hash_reset_token(reset_token),
                    "reset_password_expires_at": expires_at,
                    "updated_at": datetime.now(timezone.utc),
                }
            },
        )

        await run_in_threadpool(
            send_password_reset_email,
            user["email"],
            reset_link,
            RESET_PASSWORD_TOKEN_EXPIRE_MINUTES,
        )
        return None

    @staticmethod
    async def reset_password(token: str, new_password: str) -> None:
        """Reset a user's password with a valid one-time reset token"""
        db = await get_db()
        token_hash = AuthService.hash_reset_token(token)
        now = datetime.now(timezone.utc)

        result = await db[AUTH_COLLECTION].update_one(
            {
                "reset_password_token_hash": token_hash,
                "reset_password_expires_at": {"$gt": now},
            },
            {
                "$set": {
                    "hashed_password": AuthService.hash_password(new_password),
                    "updated_at": now,
                },
                "$unset": {
                    "reset_password_token_hash": "",
                    "reset_password_expires_at": "",
                },
            },
        )

        if result.modified_count == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired password reset token",
            )

    @staticmethod
    async def get_user_by_id(user_id: str) -> dict:
        """Get user by ID"""
        try:
            db = await get_db()
            user = await db[AUTH_COLLECTION].find_one({"_id": ObjectId(user_id)})
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=USER_NOT_FOUND
                )
            return user
        except Exception as e:
            if isinstance(e, HTTPException):
                raise
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid user ID"
            )


def build_user_response(user: dict) -> UserResponse:
    """Build a user response from a user document"""
    if not user:
        return None
    return UserResponse(
        id=str(user.get("_id")),
        email=user.get("email"),
        full_name=user.get("full_name"),
        username=user.get("username"),
        avatar_url=user.get("avatar_url"),
        is_active=user.get("is_active", True),
        created_at=user.get("created_at").isoformat() if user.get("created_at") else None
    )
