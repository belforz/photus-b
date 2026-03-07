from pydantic_settings import BaseSettings

class AppSettings(BaseSettings):
    MISTRAL_API_KEY: str
    class Config:
        env_file = ".env"

settings = AppSettings()