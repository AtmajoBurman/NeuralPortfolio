from typing import Optional
from sqlmodel import Field, SQLModel
from pydantic import field_validator

class SGPATrackerBase(SQLModel):
    semester_name: str
    grade: float

    @field_validator("grade")
    @classmethod
    def validate_grade(cls, v: float) -> float:
        if v < 0.00 or v > 10.00:
            raise ValueError("Grade must be between 0.00 and 10.00 inclusive")
        # Ensure it always has precision up to two places after the decimal
        return round(v, 2)

class SGPATracker(SGPATrackerBase, table=True):
    __tablename__ = "sgpa_tracker"

    id: Optional[int] = Field(default=None, primary_key=True)

class SGPATrackerCreate(SGPATrackerBase):
    pass

class SGPATrackerUpdate(SQLModel):
    semester_name: Optional[str] = None
    grade: Optional[float] = None

    @field_validator("grade")
    @classmethod
    def validate_grade(cls, v: Optional[float]) -> Optional[float]:
        if v is not None:
            if v < 0.00 or v > 10.00:
                raise ValueError("Grade must be between 0.00 and 10.00 inclusive")
            return round(v, 2)
        return v

class SGPATrackerRead(SGPATrackerBase):
    id: int
