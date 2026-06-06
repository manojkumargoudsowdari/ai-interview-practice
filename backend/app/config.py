from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "AI Interview Practice App"
    app_env: str = "local"
    llm_provider: str = "mock"

    class Config:
        env_file = ".env"


settings = Settings()
