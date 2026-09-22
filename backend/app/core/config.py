from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str

    GEMINI_API_KEY: str
    QDRANT_URL: str

    SEMANTIC_DUPLICATE_THRESHOLD: float = 0.78

    AWS_REGION: str = "us-east-1"
    SQS_QUEUE_URL: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )


settings = Settings()
