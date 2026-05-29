from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from typing import List

from app.database import get_session
from app.models.sgpa import SGPATracker, SGPATrackerCreate, SGPATrackerUpdate, SGPATrackerRead
from app.utils.db_helpers import touch_student_details

router = APIRouter(prefix="/sgpa", tags=["SGPA Tracker"])

@router.post("", response_model=SGPATrackerRead, status_code=status.HTTP_201_CREATED)
async def create_sgpa(sgpa_in: SGPATrackerCreate, db: AsyncSession = Depends(get_session)):
    sgpa = SGPATracker.model_validate(sgpa_in)
    db.add(sgpa)
    await db.commit()
    await db.refresh(sgpa)
    await touch_student_details(db)
    return sgpa

@router.get("", response_model=List[SGPATrackerRead])
async def list_sgpa(db: AsyncSession = Depends(get_session)):
    result = await db.execute(select(SGPATracker))
    return result.scalars().all()

@router.put("/{sgpa_id}", response_model=SGPATrackerRead)
async def update_sgpa(sgpa_id: int, sgpa_in: SGPATrackerUpdate, db: AsyncSession = Depends(get_session)):
    result = await db.execute(select(SGPATracker).where(SGPATracker.id == sgpa_id))
    sgpa = result.scalar_one_or_none()
    if not sgpa:
        raise HTTPException(status_code=404, detail="SGPA record not found")
    
    update_data = sgpa_in.model_dump(exclude_unset=True)
    for key, val in update_data.items():
        setattr(sgpa, key, val)
        
    db.add(sgpa)
    await db.commit()
    await db.refresh(sgpa)
    await touch_student_details(db)
    return sgpa

@router.delete("/{sgpa_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_sgpa(sgpa_id: int, db: AsyncSession = Depends(get_session)):
    result = await db.execute(select(SGPATracker).where(SGPATracker.id == sgpa_id))
    sgpa = result.scalar_one_or_none()
    if not sgpa:
        raise HTTPException(status_code=404, detail="SGPA record not found")
        
    await db.delete(sgpa)
    await db.commit()
    await touch_student_details(db)
