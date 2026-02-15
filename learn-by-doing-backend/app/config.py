from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application configuration."""
    
    # API Configuration
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "LearnByDoing Backend"
    DEBUG: bool = False
    
    # Database Configuration
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/learnbydoing"
    
    # OpenRouter API Configuration
    OPENROUTER_API_KEY: str = ""
    OPENROUTER_MODEL: str = "thudm/glm-4.5"  # GLM 4.5 free tier on OpenRouter
    
    # Workflow Configuration - reduced for 20 RPM limit
    MAX_ITERATIONS: int = 2
    QUALITY_THRESHOLD: float = 0.85
    
    # Resource Validation
    VALIDATE_RESOURCES: bool = True
    VALIDATION_TIMEOUT: int = 5  # seconds per URL
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
