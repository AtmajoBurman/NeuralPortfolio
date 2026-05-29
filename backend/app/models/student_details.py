from datetime import datetime, timezone
from typing import Optional
from sqlmodel import Field, SQLModel
from pydantic import field_validator, EmailStr

from sqlalchemy import Column, Text

class StudentDetailsBase(SQLModel):
    name: str = Field(max_length=100)
    profile_pic: str
    bio: str = Field(sa_column=Column(Text, nullable=False))
    gmail: str

    @field_validator("profile_pic")
    @classmethod
    def validate_profile_pic(cls, v: str) -> str:
        from app.utils.validators import validate_google_drive
        return validate_google_drive(v)

class StudentDetails(StudentDetailsBase, table=True):
    __tablename__ = "student_details"

    id: Optional[int] = Field(default=None, primary_key=True)
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc).replace(tzinfo=None))

class StudentDetailsUpdate(SQLModel):
    name: Optional[str] = Field(default=None, max_length=100)
    profile_pic: Optional[str] = None
    bio: Optional[str] = Field(default=None)
    gmail: Optional[EmailStr] = None

    @field_validator("profile_pic")
    @classmethod
    def validate_profile_pic(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            from app.utils.validators import validate_google_drive
            return validate_google_drive(v)
        return v

    @field_validator("gmail")
    @classmethod
    def convert_email_to_str(cls, v: Optional[EmailStr]) -> Optional[str]:
        if v is not None:
            return str(v)
        return v

class StudentDetailsRead(StudentDetailsBase):
    id: int
    updated_at: datetime
