from typing import Optional
from sqlmodel import Field, SQLModel
from pydantic import field_validator, AnyUrl

class ProfileTrackerBase(SQLModel):
    logo: str
    link: str

    @field_validator("logo")
    @classmethod
    def validate_logo_link(cls, v: str) -> str:
        from app.utils.validators import validate_google_drive
        return validate_google_drive(v)

class ProfileTracker(ProfileTrackerBase, table=True):
    __tablename__ = "profiles"

    id: Optional[int] = Field(default=None, primary_key=True)

class ProfileTrackerCreate(SQLModel):
    logo: str
    link: AnyUrl

    @field_validator("logo")
    @classmethod
    def validate_logo_link(cls, v: str) -> str:
        from app.utils.validators import validate_google_drive
        return validate_google_drive(v)

    @field_validator("link")
    @classmethod
    def convert_url_to_str(cls, v: AnyUrl) -> str:
        return str(v)

class ProfileTrackerUpdate(SQLModel):
    logo: Optional[str] = None
    link: Optional[AnyUrl] = None

    @field_validator("logo")
    @classmethod
    def validate_logo_link(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            from app.utils.validators import validate_google_drive
            return validate_google_drive(v)
        return v

    @field_validator("link")
    @classmethod
    def convert_url_to_str(cls, v: Optional[AnyUrl]) -> Optional[str]:
        if v is not None:
            return str(v)
        return v

class ProfileTrackerRead(ProfileTrackerBase):
    id: int
