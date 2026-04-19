from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings

load_dotenv(".env", override=True)


class AppSettings(BaseSettings):
    MISTRAL_API_KEY: str = Field(..., env="MISTRAL_API_KEY")
    HF_API_KEY: str = Field(..., env="HF_API_KEY")
    
    class Config:
        env_file = ".env"


settings = AppSettings()