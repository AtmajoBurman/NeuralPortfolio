from datetime import date, datetime, timezone
from typing import Optional
from sqlmodel import Field, SQLModel
from pydantic import field_validator, AnyUrl

class AchievementBase(SQLModel):
    name: str
    score_or_grade: Optional[str] = Field(default=None, nullable=True)
    description: str
    view_certificate: Optional[str] = Field(default=None, nullable=True)
    picture: Optional[str] = Field(default=None, nullable=True)
    linkedin_post: Optional[str] = Field(default=None, nullable=True)
    start_date: date
    end_date: Optional[date] = Field(default=None, nullable=True)
    order_index: int = Field(default=0)

    @field_validator("view_certificate")
    @classmethod
    def validate_view_certificate(cls, v: Optional[str]) -> Optional[str]:
        if v:
            from app.utils.validators import validate_google_drive
            return validate_google_drive(v)
        return v

    @field_validator("picture")
    @classmethod
    def validate_picture(cls, v: Optional[str]) -> Optional[str]:
        if v:
            from app.utils.validators import validate_google_drive
            return validate_google_drive(v)
        return v

    @field_validator("linkedin_post")
    @classmethod
    def validate_linkedin_post(cls, v: Optional[str]) -> Optional[str]:
        if v:
            from app.utils.validators import validate_linkedin
            return validate_linkedin(v)
        return v

class Achievement(AchievementBase, table=True):
    __tablename__ = "achievements"

    id: Optional[int] = Field(default=None, primary_key=True)
    date_added: datetime = Field(default_factory=lambda: datetime.now(timezone.utc).replace(tzinfo=None))

class AchievementCreate(SQLModel):
    name: str
    score_or_grade: Optional[str] = None
    description: str
    view_certificate: Optional[str] = None
    picture: Optional[str] = None
    linkedin_post: Optional[AnyUrl] = None
    start_date: date
    end_date: Optional[date] = None

    @field_validator("view_certificate")
    @classmethod
    def validate_view_certificate(cls, v: Optional[str]) -> Optional[str]:
        if v:
            from app.utils.validators import validate_google_drive
            return validate_google_drive(v)
        return v

    @field_validator("picture")
    @classmethod
    def validate_picture(cls, v: Optional[str]) -> Optional[str]:
        if v:
            from app.utils.validators import validate_google_drive
            return validate_google_drive(v)
        return v

    @field_validator("linkedin_post")
    @classmethod
    def validate_linkedin_post(cls, v: Optional[AnyUrl]) -> Optional[str]:
        if v is not None:
            from app.utils.validators import validate_linkedin
            return validate_linkedin(str(v))
        return None

class AchievementUpdate(SQLModel):
    name: Optional[str] = None
    score_or_grade: Optional[str] = None
    description: Optional[str] = None
    view_certificate: Optional[str] = None
    picture: Optional[str] = None
    linkedin_post: Optional[AnyUrl] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None

    @field_validator("view_certificate")
    @classmethod
    def validate_view_certificate(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            from app.utils.validators import validate_google_drive
            return validate_google_drive(v)
        return v

    @field_validator("picture")
    @classmethod
    def validate_picture(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            from app.utils.validators import validate_google_drive
            return validate_google_drive(v)
        return v

    @field_validator("linkedin_post")
    @classmethod
    def validate_linkedin_post(cls, v: Optional[AnyUrl]) -> Optional[str]:
        if v is not None:
            from app.utils.validators import validate_linkedin
            return validate_linkedin(str(v))
        return v

class AchievementRead(AchievementBase):
    id: int
    date_added: datetime
    score_or_grade: Optional[str] = None
    view_certificate: Optional[str] = None
    picture: Optional[str] = None
    linkedin_post: Optional[str] = None
    end_date: Optional[date] = None
