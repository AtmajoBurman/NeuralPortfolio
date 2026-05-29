from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, or_
from typing import List

from app.database import get_session
from app.models.chitchat import ChitChat, ChitChatCreate, ChitChatUpdate, ChitChatRead
from app.utils.db_helpers import touch_student_details
from app.authentication.dependencies import require_admin

router = APIRouter(prefix="/chitchat", tags=["Chit-Chat"])

@router.post("", response_model=ChitChatRead, status_code=status.HTTP_201_CREATED)
async def create_chitchat(cc_in: ChitChatCreate, db: AsyncSession = Depends(get_session), admin = Depends(require_admin)):
    cc = ChitChat.model_validate(cc_in)
    db.add(cc)
    await db.commit()
    await db.refresh(cc)
    await touch_student_details(db)
    return cc

@router.get("", response_model=List[ChitChatRead])
async def list_chitchat(db: AsyncSession = Depends(get_session)):
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    # Exclude posts where vanishing_date has passed (vanishing_date is in the past)
    # We keep posts where vanishing_date is NULL or vanishing_date > now
    stmt = select(ChitChat).where(or_(ChitChat.vanishing_date == None, ChitChat.vanishing_date > now)).order_by(ChitChat.date_added.desc())
    result = await db.execute(stmt)
    return result.scalars().all()

@router.put("/{cc_id}", response_model=ChitChatRead)
async def update_chitchat(cc_id: int, cc_in: ChitChatUpdate, db: AsyncSession = Depends(get_session), admin = Depends(require_admin)):
    result = await db.execute(select(ChitChat).where(ChitChat.id == cc_id))
    cc = result.scalar_one_or_none()
    if not cc:
        raise HTTPException(status_code=404, detail="Chit-Chat not found")
        
    update_data = cc_in.model_dump(exclude_unset=True)
    for key, val in update_data.items():
        setattr(cc, key, val)
        
    cc.date_updated = datetime.now(timezone.utc).replace(tzinfo=None)
    db.add(cc)
    await db.commit()
    await db.refresh(cc)
    await touch_student_details(db)
    return cc

@router.delete("/{cc_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_chitchat(cc_id: int, db: AsyncSession = Depends(get_session), admin = Depends(require_admin)):
    result = await db.execute(select(ChitChat).where(ChitChat.id == cc_id))
    cc = result.scalar_one_or_none()
    if not cc:
        raise HTTPException(status_code=404, detail="Chit-Chat not found")
        
    await db.delete(cc)
    await db.commit()
    await touch_student_details(db)
