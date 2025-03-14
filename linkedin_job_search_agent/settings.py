from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Settings for the LinkedIn job search agent."""

    HUGGING_FACE_TOKEN: str
    OPENAI_API_KEY: str
    GOOGLE_API_KEY: str
    GROQ_API_KEY: str
    QDRANT_API_KEY: str
    QDRANT_HOST_URL: str
    LANGSMITH_TRACING: bool = True
    LANGSMITH_PROJECT: str = "linkedin-job-search-agent"
    LANGSMITH_ENDPOINT: str
    LINKEDIN_USERNAME: str
    LINKEDIN_PASSWORD: str

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


env_settings = Settings()
