import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "Document Intake Assistant"
    APP_ENV: str = "development"
    SECRET_KEY: str = "dev_secret_key"
    
    # Database
    DATABASE_URL: str = "sqlite:///./document_intake.db"
    
    # LLM Settings
    LLM_PROVIDER: str = "mock"  # mock, openai, gemini, anthropic
    OPENAI_API_KEY: str = ""
    GEMINI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""
    
    # Email Settings (SMTP)
    EMAIL_HOST: str = "smtp.gmail.com"
    EMAIL_PORT: int = 587
    EMAIL_USERNAME: str = ""
    EMAIL_PASSWORD: str = ""
    EMAIL_FROM: str = "noreply@documentintake.com"
    
    # CORS
    ALLOWED_ORIGINS: str = "http://localhost:5173,http://localhost:3000"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

settings = Settings()
