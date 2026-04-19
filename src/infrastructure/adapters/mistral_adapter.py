import os
import logging
from typing import List, Dict, Optional, Union
from mistralai import Mistral
from infrastructure.config.settings import AppSettings
from infrastructure.config.prompts.loader import load_prompt

logger = logging.getLogger(__name__)

VALID_MODELS = {"mistral-small-2508", "magistral-small-2509"}


class APIError(Exception):
    pass

class MistralConnector:
    def __init__(
        self,
        model: str = "magistral-small-2509",
        api_key: Optional[str] = None,
    ):
        self.api_key = api_key or AppSettings().MISTRAL_API_KEY
        if not self.api_key:
            raise ValueError("Key is not defined")
        if model not in VALID_MODELS:
            raise ValueError(
                f"Invalid Model: '{model}'. Valid models: {sorted(VALID_MODELS)}"
            )
        self.model = model
        self.client = Mistral(api_key=self.api_key)

    def send_message(
        self,
        messages: List[Dict[str, str]],
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        raw: bool = False,
    ) -> Union[str, Dict]:
        try:
            resp = self.client.chat.complete(
                model=self.model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature or 0.1,
                top_p=0.9,
            )
            return resp if raw else resp.choices[0].message.content
        except Exception as e:
            logger.error(f"Error in Mistral request: {e}")
            raise APIError(str(e)) from e

    def send_message_in_portuguese(
        self,
        messages: List[Dict[str, str]],
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        raw: bool = False,
    ) -> Union[str, Dict]:
        try:
            try:
                system_content = load_prompt("portuguese")
            except Exception:
                system_content = "Responda todas as perguntas exclusivamente em português."

            system_message = {"role": "system", "content": system_content}
            injected_messages = [system_message] + messages

            resp = self.client.chat.complete(
                model=self.model,
                messages=injected_messages,
                max_tokens=max_tokens,
                temperature=temperature or 0.1,
                top_p=0.9,
            )
            return resp if raw else resp.choices[0].message.content
        except Exception as e:
            logger.error(f"Error in Mistral request: {e}")
            raise APIError(str(e)) from e