from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.database import get_session
from app.models.cgpa import CGPATracker, CGPATrackerUpdate, CGPATrackerRead
from app.utils.db_helpers import touch_student_details

router = APIRouter(prefix="/cgpa", tags=["CGPA Tracker"])

@router.get("", response_model=CGPATrackerRead)
async def get_cgpa(db: AsyncSession = Depends(get_session)):
    result = await db.execute(select(CGPATracker).where(CGPATracker.id == 1))
    cgpa = result.scalar_one_or_none()
    if not cgpa:
        raise HTTPException(status_code=404, detail="CGPA record not initialized")
    return cgpa

@router.put("", response_model=CGPATrackerRead)
async def update_cgpa(cgpa_in: CGPATrackerUpdate, db: AsyncSession = Depends(get_session)):
    result = await db.execute(select(CGPATracker).where(CGPATracker.id == 1))
    cgpa = result.scalar_one_or_none()
    if not cgpa:
        raise HTTPException(status_code=404, detail="CGPA record not initialized")
    
    update_data = cgpa_in.model_dump(exclude_unset=True)
    for key, val in update_data.items():
        setattr(cgpa, key, val)
        
    db.add(cgpa)
    await db.commit()
    await db.refresh(cgpa)
    await touch_student_details(db)
    return cgpa
