from fastapi import Header, HTTPException

async def get_current_user_id(authorization: str = Header(default="Bearer user_123456789")):
    # TODO: Thay thế bằng logic decode JWT token thật sự
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid token")
    return authorization.replace("Bearer ", "")