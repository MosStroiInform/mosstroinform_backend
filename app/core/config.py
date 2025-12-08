from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore",  # игнорируем неиспользуемые переменные окружения (POSTGRES_*, APP_PORT и т.д.)
    )

    # Application
    APP_NAME: str = "MosStroiInform API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Database (postgresql+psycopg для использования psycopg3)
    DATABASE_URL: str = "postgresql+psycopg://user:password@localhost:5432/mosstroinform_db"
    
    # Security (для будущей интеграции)
    SECRET_KEY: str = "your-secret-key-here-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30


settings = Settings()

