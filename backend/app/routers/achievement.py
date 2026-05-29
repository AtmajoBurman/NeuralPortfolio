from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from typing import List

from app.database import get_session
from app.models.achievement import Achievement, AchievementCreate, AchievementUpdate, AchievementRead
from app.utils.db_helpers import touch_student_details
from app.authentication.dependencies import require_admin

from pydantic import BaseModel

class ReorderRequest(BaseModel):
    item_ids: List[int]

router = APIRouter(prefix="/achievements", tags=["Achievements"])

@router.post("", response_model=AchievementRead, status_code=status.HTTP_201_CREATED)
async def create_achievement(ach_in: AchievementCreate, db: AsyncSession = Depends(get_session), admin = Depends(require_admin)):
    ach = Achievement.model_validate(ach_in)
    db.add(ach)
    await db.commit()
    await db.refresh(ach)
    await touch_student_details(db)
    return ach

@router.get("", response_model=List[AchievementRead])
async def list_achievements(db: AsyncSession = Depends(get_session)):
    # Arrange achievements by manual order_index, fallback to decreasing order of the date added
    result = await db.execute(select(Achievement).order_by(Achievement.order_index.asc(), Achievement.date_added.desc()))
    return result.scalars().all()

@router.put("/reorder", response_model=dict)
async def reorder_achievements(request: ReorderRequest, db: AsyncSession = Depends(get_session), admin = Depends(require_admin)):
    for index, item_id in enumerate(request.item_ids):
        result = await db.execute(select(Achievement).where(Achievement.id == item_id))
        ach = result.scalar_one_or_none()
        if ach:
            ach.order_index = index
            db.add(ach)
    await db.commit()
    await touch_student_details(db)
    return {"status": "success"}

@router.put("/{ach_id}", response_model=AchievementRead)
async def update_achievement(ach_id: int, ach_in: AchievementUpdate, db: AsyncSession = Depends(get_session), admin = Depends(require_admin)):
    result = await db.execute(select(Achievement).where(Achievement.id == ach_id))
    ach = result.scalar_one_or_none()
    if not ach:
        raise HTTPException(status_code=404, detail="Achievement not found")
        
    update_data = ach_in.model_dump(exclude_unset=True)
    for key, val in update_data.items():
        setattr(ach, key, val)
        
    db.add(ach)
    await db.commit()
    await db.refresh(ach)
    await touch_student_details(db)
    return ach

@router.delete("/{ach_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_achievement(ach_id: int, db: AsyncSession = Depends(get_session), admin = Depends(require_admin)):
    result = await db.execute(select(Achievement).where(Achievement.id == ach_id))
    ach = result.scalar_one_or_none()
    if not ach:
        raise HTTPException(status_code=404, detail="Achievement not found")
        
    await db.delete(ach)
    await db.commit()
    await touch_student_details(db)
