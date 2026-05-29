from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from typing import List

from app.database import get_session
from app.models.profile import ProfileTracker, ProfileTrackerCreate, ProfileTrackerUpdate, ProfileTrackerRead
from app.utils.db_helpers import touch_student_details

router = APIRouter(prefix="/profiles", tags=["Profiles Tracker"])

@router.post("", response_model=ProfileTrackerRead, status_code=status.HTTP_201_CREATED)
async def create_profile(profile_in: ProfileTrackerCreate, db: AsyncSession = Depends(get_session)):
    profile = ProfileTracker.model_validate(profile_in)
    db.add(profile)
    await db.commit()
    await db.refresh(profile)
    await touch_student_details(db)
    return profile

@router.get("", response_model=List[ProfileTrackerRead])
async def list_profiles(db: AsyncSession = Depends(get_session)):
    result = await db.execute(select(ProfileTracker))
    return result.scalars().all()

@router.put("/{profile_id}", response_model=ProfileTrackerRead)
async def update_profile(profile_id: int, profile_in: ProfileTrackerUpdate, db: AsyncSession = Depends(get_session)):
    result = await db.execute(select(ProfileTracker).where(ProfileTracker.id == profile_id))
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile record not found")
        
    update_data = profile_in.model_dump(exclude_unset=True)
    for key, val in update_data.items():
        setattr(profile, key, val)
        
    db.add(profile)
    await db.commit()
    await db.refresh(profile)
    await touch_student_details(db)
    return profile

@router.delete("/{profile_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_profile(profile_id: int, db: AsyncSession = Depends(get_session)):
    result = await db.execute(select(ProfileTracker).where(ProfileTracker.id == profile_id))
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile record not found")
        
    await db.delete(profile)
    await db.commit()
    await touch_student_details(db)
