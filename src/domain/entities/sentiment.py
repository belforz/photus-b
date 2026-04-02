from dataclasses import dataclass
from typing import Optional

from src.domain.entities.score import Score
from src.domain.entities.text_input import TextInput


@dataclass(frozen=True)
class Sentiment:
    """Represents the complete sentiment analysis for a text."""

    score: Score
    label: str
    text_input: Optional[TextInput] = None
    emotion: Optional[str] = None
    cosine_similarity: Optional[float] = None
