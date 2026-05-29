from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.database import get_session
from app.models.student_details import StudentDetails, StudentDetailsUpdate, StudentDetailsRead
from app.authentication.dependencies import require_admin

router = APIRouter(prefix="/student_details", tags=["Student Details"])

@router.get("", response_model=StudentDetailsRead)
async def get_student_details(db: AsyncSession = Depends(get_session)):
    result = await db.execute(select(StudentDetails).where(StudentDetails.id == 1))
    student = result.scalar_one_or_none()
    if not student:
        raise HTTPException(status_code=404, detail="Student Details record not initialized")
    return student

@router.put("", response_model=StudentDetailsRead)
async def update_student_details(student_in: StudentDetailsUpdate, db: AsyncSession = Depends(get_session), admin = Depends(require_admin)):
    result = await db.execute(select(StudentDetails).where(StudentDetails.id == 1))
    student = result.scalar_one_or_none()
    if not student:
        raise HTTPException(status_code=404, detail="Student Details record not initialized")
        
    update_data = student_in.model_dump(exclude_unset=True)
    for key, val in update_data.items():
        setattr(student, key, val)
        
    # Always update the updated_at field for student details
    student.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)
    
    db.add(student)
    await db.commit()
    await db.refresh(student)
    return student
