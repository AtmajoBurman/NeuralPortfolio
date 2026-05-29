from fastapi import APIRouter, Request, Depends, HTTPException, status, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
import os

from app.database import get_session
from app.models.admin import AdminUser
from app.authentication.auth_utils import verify_password, create_access_token, get_password_hash
from app.authentication.dependencies import require_admin
from pydantic import BaseModel

class PasswordUpdate(BaseModel):
    new_password: str

router = APIRouter()
templates = Jinja2Templates(directory=os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates"))

@router.get("/login", response_class=HTMLResponse)
async def login_get(request: Request):
    return templates.TemplateResponse(request=request, name="login.html")

@router.post("/login")
async def login_post(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: AsyncSession = Depends(get_session)
):
    result = await db.execute(select(AdminUser).where(AdminUser.username == username))
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(password, user.hashed_password):
        return templates.TemplateResponse(
            request=request,
            name="login.html", 
            context={"error": "Invalid username or password"}, 
            status_code=401
        )
        
    access_token = create_access_token(data={"sub": user.username, "role": user.role})
    
    response = RedirectResponse(url="/admin", status_code=status.HTTP_303_SEE_OTHER)
    # Set HttpOnly cookie
    response.set_cookie(
        key="access_token",
        value=f"{access_token}",
        httponly=True,
        samesite="lax",
        max_age=3600  # 1 hour
    )
    return response

@router.get("/logout")
async def logout():
    response = RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie("access_token")
    return response

@router.put("/update-password")
async def update_password(
    pwd_update: PasswordUpdate,
    db: AsyncSession = Depends(get_session),
    admin: AdminUser = Depends(require_admin)
):
    admin.hashed_password = get_password_hash(pwd_update.new_password)
    db.add(admin)
    await db.commit()
    return {"message": "Password updated successfully"}
