import logging
from typing import List, Dict, Optional, Union
from litellm import completion
from infrastructure.config.settings import settings

logger = logging.getLogger(__name__)



class APIError(Exception):
    pass

class LLMConnector:
    def __init__(self, **kwargs):
        self.model = settings.LLM_MODEL_CURRENT_NAME
        self._api_key = settings.MISTRAL_API_KEY
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
        
    