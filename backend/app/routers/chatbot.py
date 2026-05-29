from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
import asyncio

from app.chatbot.code import get_chatbot_response
from app.database import get_session
from app.models.settings import Settings
from app.authentication.dependencies import require_admin
from app.chatbot.generic_response import GENERIC_RESPONSE

router = APIRouter(prefix="/chatbot", tags=["Chatbot"])

class ChatRequest(BaseModel):
    message: str

class SmartModeRequest(BaseModel):
    smart_mode: bool

@router.get("/smart-mode")
async def get_smart_mode(db: AsyncSession = Depends(get_session)):
    result = await db.execute(select(Settings).where(Settings.id == 1))
    settings = result.scalar_one_or_none()
    if settings:
        return {"smart_mode": settings.smart_mode}
    return {"smart_mode": True}

@router.post("/smart-mode")
async def update_smart_mode(
    request: SmartModeRequest, 
    db: AsyncSession = Depends(get_session),
    admin_user = Depends(require_admin)
):
    result = await db.execute(select(Settings).where(Settings.id == 1))
    settings = result.scalar_one_or_none()
    
    if settings:
        settings.smart_mode = request.smart_mode
    else:
        settings = Settings(id=1, smart_mode=request.smart_mode)
        db.add(settings)
        
    await db.commit()
    return {"status": "success", "smart_mode": settings.smart_mode}

@router.post("")
async def chat(request: ChatRequest, db: AsyncSession = Depends(get_session)):
    # Check smart mode toggle
    result = await db.execute(select(Settings).where(Settings.id == 1))
    settings = result.scalar_one_or_none()
    
    if settings and not settings.smart_mode:
        return {
            "reply": GENERIC_RESPONSE.strip(),
            "status": "success"
        }
        
    # Run the synchronous Langchain call in a background thread to avoid blocking the event loop
    response_text = await asyncio.to_thread(get_chatbot_response, request.message)
    return {
        "reply": response_text,
        "status": "success"
    }
