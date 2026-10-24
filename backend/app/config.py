from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

_backend_env = Path(__file__).resolve().parent.parent / ".env"
_root_env = Path(__file__).resolve().parent.parent.parent / ".env"

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", "backend/.env", str(_backend_env), str(_root_env)),
        extra="ignore"
    )

    PROJECT_NAME: str = "YojanaSetu"
    VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api"
    
    # Database
    DATABASE_URL: str = "sqlite:///./yojanasetu.db"
    
    # Hugging Face Inference Providers Configuration
    HF_TOKEN: str = Field(default="", description="Hugging Face User Access Token")
    HF_MODEL: str = Field(default="meta-llama/Llama-3.3-70B-Instruct", description="Hugging Face Model ID")
    HF_PROVIDER: str = Field(default="", description="Optional provider override e.g. together, sambanova, novita, groq")

    # OpenAI API configuration (optional fallback)
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

    @property
    def effective_hf_token(self) -> str:
        """Returns the configured HF token, also detecting if passed in OPENAI_API_KEY."""
        if self.HF_TOKEN and not self.HF_TOKEN.startswith("hf_your_"):
            return self.HF_TOKEN.strip()
        if self.OPENAI_API_KEY and self.OPENAI_API_KEY.startswith("hf_"):
            return self.OPENAI_API_KEY.strip()
        return ""

    @property
    def effective_hf_model(self) -> str:
        """Returns the configured HF model, with intelligent fallback."""
        if self.HF_MODEL and self.HF_MODEL.strip():
            return self.HF_MODEL.strip()
        if self.OPENAI_MODEL and "/" in self.OPENAI_MODEL:
            return self.OPENAI_MODEL.strip()
        return "meta-llama/Llama-3.3-70B-Instruct"

    @property
    def is_ai_configured(self) -> bool:
        """Indicates if any LLM service (Hugging Face or OpenAI) is configured."""
        return bool(self.effective_hf_token or (self.OPENAI_API_KEY and not self.OPENAI_API_KEY.startswith("your_")))

settings = Settings()
