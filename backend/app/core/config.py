import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

# Base Directory of backend
BASE_DIR = Path(__file__).resolve().parent.parent.parent

class Settings(BaseSettings):
    MONGODB_URI: str = ""
    MONGODB_DB_NAME: str = "smart_campus"
    JWT_SECRET: str = "supersecretjwtkey_smart_campus_digital_twin_2026"
    JWT_EXPIRE_MINUTES: int = 480
    CORS_ORIGINS: str = "http://localhost:5173"
    USE_EMBEDDED_DB: bool = False

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
