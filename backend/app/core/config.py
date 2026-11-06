from typing import List, Union
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # App & Environment
    PROJECT_NAME: str = "LabGuard-X"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    API_V1_STR: str = "/api/v1"

    # Server binding
    HOST: str = "127.0.0.1"
    PORT: int = 8000

    # Database Configuration (Supabase PostgreSQL / SQLite fallback)
    DATABASE_URL: str = "sqlite:///./lab_guard.db"
    DB_ECHO: bool = False
    DB_POOL_PRE_PING: bool = True

    # Supabase Credentials
    SUPABASE_URL: str = ""
    SUPABASE_ANON_KEY: str = ""
    SUPABASE_SERVICE_ROLE_KEY: str = ""

    # Security & JWT Tokens
    SECRET_KEY: str = "labguard-super-secret-key-change-in-production-2026!#*&"
    JWT_SECRET_KEY: str = "your-super-secret-jwt-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # CORS Configuration
    CORS_ORIGINS: Union[str, List[str]] = ["*"]

    # IoT Gateway & Hardware Auth
    IOT_DEFAULT_API_KEY: str = "labguard-iot-secret-device-key-2026"
    IOT_HEARTBEAT_TIMEOUT_SECONDS: int = 120

    # AI & Anomaly Detection Settings
    AI_ANOMALY_THRESHOLD: float = 0.85
    AI_MODEL_DIRECTORY: str = "./ml_models"

    # Default Super Admin Setup
    FIRST_SUPERUSER_EMAIL: str = "admin@labguard.local"
    FIRST_SUPERUSER_PASSWORD: str = "Admin@123456"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )


settings = Settings()
