from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/job_matcher"
    
    # Application
    APP_ENV: str = "development"
    DEBUG: bool = True
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]
    
    # Upload Settings
    MAX_UPLOAD_SIZE: int = 5242880  # 5MB
    UPLOAD_DIR: str = "./uploads"
    
    # AI Model Settings
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    SIMILARITY_THRESHOLD: float = 0.3  # Minimum score to show a job
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production-min-32-characters-long"
    
    class Config:
        env_file = ".env"


settings = Settings()
