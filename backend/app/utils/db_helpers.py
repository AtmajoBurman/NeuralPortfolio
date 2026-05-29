from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

async def touch_student_details(db: AsyncSession):
    """
    Updates the updated_at timestamp of the student_details record with id = 1.
    Called automatically after any database write operation.
    """
    from app.models.student_details import StudentDetails
    
    result = await db.execute(select(StudentDetails).where(StudentDetails.id == 1))
    student = result.scalar_one_or_none()
    if student:
        student.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)
        db.add(student)
        # We use flush to write to the session, which will be committed in the route handler.
        # Alternatively, we commit here, but since the route handler might commit, 
        # doing db.add(student) followed by await db.flush() is safer as it maintains
        # the same transaction boundary. Let's commit here directly or flush.
        # Committing here is clean as we can run it in a separate block or as part of the route.
        # Let's commit to ensure it's saved.
        await db.commit()
