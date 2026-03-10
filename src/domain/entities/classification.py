from dataclasses import dataclass
from typing import List, Optional

from src.domain.entities.sentiment import Sentiment
from src.domain.entities.tag import Tag
from src.domain.entities.text_input import TextInput


@dataclass()
class Classification:
    """
    Represents the complete result of an NLP classification process for a given text.
    It acts as an aggregate root for the analysis results.
    """
    input_text: TextInput
    tags: List[Tag]
    sentiment: Optional[Sentiment] = None
