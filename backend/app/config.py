from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "AI Interview Practice App"
    app_env: str = "local"
    llm_provider: str = "mock"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.1:8b"
    llm_timeout_seconds: int = 60

    class Config:
        env_file = ".env"


settings = Settings()
