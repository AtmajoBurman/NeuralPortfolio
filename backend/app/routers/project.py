from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from typing import List

from app.database import get_session
from app.models.project import Project, ProjectCreate, ProjectUpdate, ProjectRead
from app.utils.db_helpers import touch_student_details
from app.authentication.dependencies import require_admin

from pydantic import BaseModel

class ReorderRequest(BaseModel):
    item_ids: List[int]

router = APIRouter(prefix="/projects", tags=["Projects"])

@router.post("", response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
async def create_project(project_in: ProjectCreate, db: AsyncSession = Depends(get_session), admin = Depends(require_admin)):
    project = Project.model_validate(project_in)
    db.add(project)
    await db.commit()
    await db.refresh(project)
    await touch_student_details(db)
    return project

@router.get("", response_model=List[ProjectRead])
async def list_projects(db: AsyncSession = Depends(get_session)):
    # Arrange projects by manual order_index, fallback to decreasing order of the date added
    result = await db.execute(select(Project).order_by(Project.order_index.asc(), Project.date_added.desc()))
    return result.scalars().all()

@router.put("/reorder", response_model=dict)
async def reorder_projects(request: ReorderRequest, db: AsyncSession = Depends(get_session), admin = Depends(require_admin)):
    for index, item_id in enumerate(request.item_ids):
        result = await db.execute(select(Project).where(Project.id == item_id))
        project = result.scalar_one_or_none()
        if project:
            project.order_index = index
            db.add(project)
    await db.commit()
    await touch_student_details(db)
    return {"status": "success"}

@router.put("/{project_id}", response_model=ProjectRead)
async def update_project(project_id: int, project_in: ProjectUpdate, db: AsyncSession = Depends(get_session), admin = Depends(require_admin)):
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
        
    update_data = project_in.model_dump(exclude_unset=True)
    for key, val in update_data.items():
        setattr(project, key, val)
        
    db.add(project)
    await db.commit()
    await db.refresh(project)
    await touch_student_details(db)
    return project

@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(project_id: int, db: AsyncSession = Depends(get_session), admin = Depends(require_admin)):
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
        
    await db.delete(project)
    await db.commit()
    await touch_student_details(db)
