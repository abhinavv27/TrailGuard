from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///../../data/trailguard.db"
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    CORS_ORIGINS: str = "http://localhost:3000"
    LLM_PROVIDER: str = ""
    LLM_API_KEY: str = ""
    DEMO_MODE: bool = True
    UPLOAD_MAX_SIZE_MB: int = 50
    STRUCTURING_THRESHOLD: float = 10000.0
    STRUCTURING_WINDOW_HOURS: int = 24

    model_config = {"env_file": ".env", "case_sensitive": False}


settings = Settings()
