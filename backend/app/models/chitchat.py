from datetime import datetime, timezone
from typing import Optional
from sqlmodel import Field, SQLModel
from pydantic import field_validator, AnyUrl

class ChitChatBase(SQLModel):
    link: Optional[str] = None
    description: str = Field(max_length=280)
    vanishing_date: Optional[datetime] = None

class ChitChat(ChitChatBase, table=True):
    __tablename__ = "chit_chat"

    id: Optional[int] = Field(default=None, primary_key=True)
    date_added: datetime = Field(default_factory=lambda: datetime.now(timezone.utc).replace(tzinfo=None))
    date_updated: datetime = Field(default_factory=lambda: datetime.now(timezone.utc).replace(tzinfo=None))

class ChitChatCreate(SQLModel):
    link: Optional[AnyUrl] = None
    description: str = Field(max_length=280)
    vanishing_date: Optional[datetime] = None

    @field_validator("link")
    @classmethod
    def convert_url_to_str(cls, v: Optional[AnyUrl]) -> Optional[str]:
        if v is not None:
            return str(v)
        return v

    @field_validator("vanishing_date")
    @classmethod
    def make_naive_datetime(cls, v: Optional[datetime]) -> Optional[datetime]:
        if v is not None and v.tzinfo is not None:
            return v.astimezone(timezone.utc).replace(tzinfo=None)
        return v

class ChitChatUpdate(SQLModel):
    link: Optional[AnyUrl] = None
    description: Optional[str] = Field(default=None, max_length=280)
    vanishing_date: Optional[datetime] = None

    @field_validator("link")
    @classmethod
    def convert_url_to_str(cls, v: Optional[AnyUrl]) -> Optional[str]:
        if v is not None:
            return str(v)
        return v

    @field_validator("vanishing_date")
    @classmethod
    def make_naive_datetime(cls, v: Optional[datetime]) -> Optional[datetime]:
        if v is not None and v.tzinfo is not None:
            return v.astimezone(timezone.utc).replace(tzinfo=None)
        return v

class ChitChatRead(ChitChatBase):
    id: int
    date_added: datetime
    date_updated: datetime
