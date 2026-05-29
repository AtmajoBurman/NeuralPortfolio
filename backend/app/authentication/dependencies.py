from fastapi import Request, HTTPException, Depends, status
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from .auth_utils import decode_token
from app.models.admin import AdminUser
from app.database import get_session

async def get_current_user(request: Request, db: AsyncSession = Depends(get_session)) -> AdminUser:
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    
    # Strip "Bearer " if present
    if token.startswith("Bearer "):
        token = token.split(" ")[1]

    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")
        
    username: str = payload.get("sub")
    if username is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")
        
    result = await db.execute(select(AdminUser).where(AdminUser.username == username))
    user = result.scalar_one_or_none()
    
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
        
    return user

async def require_admin(request: Request, db: AsyncSession = Depends(get_session)) -> AdminUser:
    user = await get_current_user(request, db)
    if user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough privileges")
    return user
