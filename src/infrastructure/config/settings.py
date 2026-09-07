from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings

load_dotenv(".env", override=True)


class AppSettings(BaseSettings):
    MISTRAL_API_KEY: str = Field(..., env="MISTRAL_API_KEY")
    HF_API_KEY: str = Field(..., env="HF_API_KEY")
    LLM_VALID_MODELS: list[str] = Field(..., env="LLM_VALID_MODELS")
    LLM_MODEL_CURRENT_NAME: str = Field(default="mistral/ministral-14b-latest", env="LLM_MODEL_CURRENT_NAME")
    LLM_MODEL_CURRENT_TEMPERATURE: float = Field(default=0.1, env="LLM_MODEL_CURRENT_TEMPERATURE")
    LLM_DEEPSEEK_API_KEY: str = Field(default="", env="LLM_DEEPSEEK_API_KEY")
    LLM_CLAUDE_API_KEY: str = Field(default="", env="LLM_CLAUDE_API_KEY")
    LLM_GEMINI_API_KEY: str = Field(default="", env="LLM_GEMINI_API_KEY")
    LLM_LLAMA_API_KEY: str = Field(default="", env="LLM_LLAMA_API_KEY")
    LLM_GITHUB_API_KEY: str = Field(default="", env="LLM_GITHUB_API_KEY")
    LLM_OPENROUTER_API_KEY: str = Field(default="", env="LLM_OPENROUTER_API_KEY")
    LLM_KIMI_API_KEY: str = Field(default="", env="LLM_KIMI_API_KEY")

    class Config:
        env_file = ".env"


settings = AppSettings()