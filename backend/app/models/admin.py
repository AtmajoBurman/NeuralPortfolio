from sqlmodel import SQLModel, Field

class AdminUser(SQLModel, table=True):
    __tablename__ = "admin_users"
    
    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True, max_length=100)
    hashed_password: str
    role: str = Field(default="admin", max_length=50)
