import os
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    PROJECT_NAME: str = "YojanaSetu"
    VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api"
    
    # Database
    DATABASE_URL: str = "sqlite:///./yojanasetu.db"
    
    # OpenAI API configuration
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"
    
    # CORS Origin
    FRONTEND_ORIGIN: str = "http://localhost:8000,http://127.0.0.1:8000,http://localhost:3000,http://127.0.0.1:5500,null"
    
    # JWT & Auth
    JWT_SECRET: str = "super_secret_jwt_key_change_in_production_min_32_chars"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    
    @property
    def cors_origins(self) -> List[str]:
        return [origin.strip() for origin in self.FRONTEND_ORIGIN.split(",") if origin.strip()]

settings = Settings()
