import logging
from typing import List, Dict, Optional, Union
from litellm import completion
from infrastructure.config.settings import settings

logger = logging.getLogger(__name__)



class APIError(Exception):
    pass

_PROVIDER_API_KEYS = {
    "mistral": lambda: settings.MISTRAL_API_KEY,
    "deepseek": lambda: settings.LLM_DEEPSEEK_API_KEY,
    "claude": lambda: settings.LLM_CLAUDE_API_KEY,
    "anthropic": lambda: settings.LLM_CLAUDE_API_KEY,
    "gemini": lambda: settings.LLM_GEMINI_API_KEY,
    "groq": lambda: settings.LLM_LLAMA_API_KEY,
    "huggingface": lambda: settings.HF_API_KEY,
    "github": lambda: settings.LLM_GITHUB_API_KEY,
    "openrouter": lambda: settings.LLM_OPENROUTER_API_KEY,
    "kimi": lambda: settings.LLM_KIMI_API_KEY,
}


def _resolve_api_key(model: str) -> Optional[str]:
    """Pick the right settings field for whichever provider prefixes `model` (e.g. 'deepseek/...').

    litellm can auto-detect keys from provider-specific env var names (MISTRAL_API_KEY,
    DEEPSEEK_API_KEY, ...), but this project only declares the LLM_* names in AppSettings
    (which forbids unrecognized .env entries) — so we resolve and pass the key explicitly
    instead of relying on litellm's own env var convention.
    """
    provider = model.split("/", 1)[0] if "/" in model else model
    getter = _PROVIDER_API_KEYS.get(provider)
    return getter() if getter else None


class LLMConnector:
    def __init__(self, **kwargs):
        self.model = settings.LLM_MODEL_CURRENT_NAME
        self._api_key = _resolve_api_key(self.model)
        if not self._api_key:
            raise ValueError("API key is missing")
        self.extra_config = kwargs
        self.temperature = settings.LLM_MODEL_CURRENT_TEMPERATURE

    def send_message(self, messages: List[Dict[str, str]], temperature: Optional[float] = None, raw: bool = False) -> Union[str, Dict]:
        try:
            logger.info(f"Sending message: {messages}")
            response = completion(
                model = self.model,
                messages = messages,
                api_key = self._api_key,
                temperature = temperature if temperature is not None else self.temperature,
            )
            if raw:
                logger.info(f"Raw response: {response}")
                return response
            formated_response = response.get("choices", [{}])[0].get("message", {}).get("content", "")
            logger.info(f"Formatted response: {formated_response}")
            return formated_response
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            raise APIError(str(e))
        
    