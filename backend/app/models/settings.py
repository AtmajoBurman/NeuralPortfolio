from sqlmodel import Field, SQLModel
from typing import Optional

class Settings(SQLModel, table=True):
    __tablename__ = "settings"

    id: Optional[int] = Field(default=None, primary_key=True)
    smart_mode: bool = Field(default=True)
