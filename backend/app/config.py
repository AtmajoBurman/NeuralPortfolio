import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    postgres_url: str
    allowed_origins: str

    model_config = SettingsConfigDict(
        # The .env file is located at the root of the project (two levels up from backend/app/config.py)
        env_file=os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
