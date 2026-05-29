from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel.ext.asyncio.session import AsyncSession
import os

from app.database import get_session
from app.authentication.dependencies import get_current_user, require_admin

router = APIRouter()
templates = Jinja2Templates(directory=os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates"))

@router.get("/admin", response_class=HTMLResponse)
async def admin_portal(request: Request, db: AsyncSession = Depends(get_session)):
    try:
        user = await get_current_user(request, db)
    except HTTPException:
        return RedirectResponse(url="/login", status_code=303)
        
    return templates.TemplateResponse(request=request, name="admin.html", context={"username": user.username})

@router.get("/admin/projects", response_class=HTMLResponse)
async def admin_projects(request: Request, db: AsyncSession = Depends(get_session)):
    try:
        user = await get_current_user(request, db)
    except HTTPException:
        return RedirectResponse(url="/login", status_code=303)
    return templates.TemplateResponse(request=request, name="admin-projects.html", context={"username": user.username})

@router.get("/admin/achievements", response_class=HTMLResponse)
async def admin_achievements(request: Request, db: AsyncSession = Depends(get_session)):
    try:
        user = await get_current_user(request, db)
    except HTTPException:
        return RedirectResponse(url="/login", status_code=303)
    return templates.TemplateResponse(request=request, name="admin-achievements.html", context={"username": user.username})

@router.get("/admin/chitchat", response_class=HTMLResponse)
async def admin_chitchat(request: Request, db: AsyncSession = Depends(get_session)):
    try:
        user = await get_current_user(request, db)
    except HTTPException:
        return RedirectResponse(url="/login", status_code=303)
    return templates.TemplateResponse(request=request, name="admin-chitchat.html", context={"username": user.username})
