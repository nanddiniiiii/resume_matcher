"""Environment configuration, independent of the shell's working directory."""
from pathlib import Path
from typing import List
import secrets
from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parents[1]

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=BACKEND_DIR / ".env", extra="ignore")
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/job_matcher"
    APP_ENV: str = "development"
    DEBUG: bool = False
    API_HOST: str = "127.0.0.1"
    API_PORT: int = 8000
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]
    MAX_UPLOAD_SIZE: int = Field(default=5242880, gt=0)
    UPLOAD_DIR: str = str(BACKEND_DIR / "uploads")
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    SIMILARITY_THRESHOLD: float = Field(default=0.3, ge=0, le=1)
    ADMIN_EMAILS: List[str] = []
    SECRET_KEY: str = ""

    @model_validator(mode="after")
    def validate_secret(self):
        placeholder = self.SECRET_KEY.startswith(("your-secret", "replace-with"))
        if not self.SECRET_KEY or placeholder or len(self.SECRET_KEY) < 32:
            if self.APP_ENV.lower() == "production":
                raise ValueError("Production requires a random SECRET_KEY of at least 32 characters")
            self.SECRET_KEY = secrets.token_urlsafe(48)
        return self

settings = Settings()
