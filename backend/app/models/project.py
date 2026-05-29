from datetime import date, datetime, timezone
from typing import Optional
from sqlmodel import Field, SQLModel
from pydantic import field_validator, AnyUrl

class ProjectBase(SQLModel):
    project_name: str
    project_category: str
    tech_stack: str
    project_description: str
    video_link: Optional[str] = Field(default=None, nullable=True)
    github_repo: Optional[str] = Field(default=None, nullable=True)
    deployed_link: Optional[str] = Field(default=None, nullable=True)
    linkedin_post: Optional[str] = Field(default=None, nullable=True)
    start_date: date
    end_date: Optional[date] = Field(default=None, nullable=True)
    order_index: int = Field(default=0)

    @field_validator("video_link")
    @classmethod
    def validate_video_link(cls, v: Optional[str]) -> Optional[str]:
        if v:
            from app.utils.validators import validate_youtube
            return validate_youtube(v)
        return v

    @field_validator("github_repo")
    @classmethod
    def validate_github_link(cls, v: Optional[str]) -> Optional[str]:
        if v:
            from app.utils.validators import validate_github
            return validate_github(v)
        return v

    @field_validator("linkedin_post")
    @classmethod
    def validate_linkedin_link(cls, v: Optional[str]) -> Optional[str]:
        if v:
            from app.utils.validators import validate_linkedin
            return validate_linkedin(v)
        return v

class Project(ProjectBase, table=True):
    __tablename__ = "projects"

    id: Optional[int] = Field(default=None, primary_key=True)
    date_added: datetime = Field(default_factory=lambda: datetime.now(timezone.utc).replace(tzinfo=None))

class ProjectCreate(SQLModel):
    project_name: str
    project_category: str
    tech_stack: str
    project_description: str
    video_link: Optional[str] = None
    github_repo: Optional[AnyUrl] = None
    deployed_link: Optional[AnyUrl] = None
    linkedin_post: Optional[AnyUrl] = None
    start_date: date
    end_date: Optional[date] = None

    @field_validator("video_link")
    @classmethod
    def validate_video_link(cls, v: Optional[str]) -> Optional[str]:
        if v:
            from app.utils.validators import validate_youtube
            return validate_youtube(v)
        return v

    @field_validator("github_repo")
    @classmethod
    def validate_github_link(cls, v: Optional[AnyUrl]) -> Optional[str]:
        if v is not None:
            from app.utils.validators import validate_github
            return validate_github(str(v))
        return None

    @field_validator("deployed_link")
    @classmethod
    def validate_deployed_link(cls, v: Optional[AnyUrl]) -> Optional[str]:
        if v is not None:
            return str(v)
        return None

    @field_validator("linkedin_post")
    @classmethod
    def validate_linkedin_link(cls, v: Optional[AnyUrl]) -> Optional[str]:
        if v is not None:
            from app.utils.validators import validate_linkedin
            return validate_linkedin(str(v))
        return None

class ProjectUpdate(SQLModel):
    project_name: Optional[str] = None
    project_category: Optional[str] = None
    tech_stack: Optional[str] = None
    project_description: Optional[str] = None
    video_link: Optional[str] = None
    github_repo: Optional[AnyUrl] = None
    deployed_link: Optional[AnyUrl] = None
    linkedin_post: Optional[AnyUrl] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None

    @field_validator("video_link")
    @classmethod
    def validate_video_link(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            from app.utils.validators import validate_youtube
            return validate_youtube(v)
        return v

    @field_validator("github_repo")
    @classmethod
    def validate_github_link(cls, v: Optional[AnyUrl]) -> Optional[str]:
        if v is not None:
            from app.utils.validators import validate_github
            return validate_github(str(v))
        return v

    @field_validator("deployed_link")
    @classmethod
    def validate_deployed_link(cls, v: Optional[AnyUrl]) -> Optional[str]:
        if v is not None:
            return str(v)
        return v

    @field_validator("linkedin_post")
    @classmethod
    def validate_linkedin_link(cls, v: Optional[AnyUrl]) -> Optional[str]:
        if v is not None:
            from app.utils.validators import validate_linkedin
            return validate_linkedin(str(v))
        return v

class ProjectRead(ProjectBase):
    id: int
    date_added: datetime
