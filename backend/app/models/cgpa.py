from typing import Optional
from sqlmodel import Field, SQLModel
from pydantic import field_validator

class CGPATrackerBase(SQLModel):
    cgpa: str = Field(default="CGPA")
    grade: float

    @field_validator("grade")
    @classmethod
    def validate_grade(cls, v: float) -> float:
        if v < 0.00 or v > 10.00:
            raise ValueError("Grade must be between 0.00 and 10.00 inclusive")
        return round(v, 2)

class CGPATracker(CGPATrackerBase, table=True):
    __tablename__ = "cgpa_tracker"

    id: Optional[int] = Field(default=None, primary_key=True)

class CGPATrackerUpdate(SQLModel):
    cgpa: Optional[str] = "CGPA"
    grade: Optional[float] = None

    @field_validator("grade")
    @classmethod
    def validate_grade(cls, v: Optional[float]) -> Optional[float]:
        if v is not None:
            if v < 0.00 or v > 10.00:
                raise ValueError("Grade must be between 0.00 and 10.00 inclusive")
            return round(v, 2)
        return v

class CGPATrackerRead(CGPATrackerBase):
    id: int
