from dataclasses import dataclass
from typing import Optional

from domain.entities.score import Score
from domain.entities.text_input import TextInput


@dataclass(frozen=True)
class Sentiment:
    """Represents the complete sentiment analysis for a text."""

    score: Score
    label: str
    text_input: Optional[TextInput] = None
    emotion: Optional[str] = None
    cosine_similarity: Optional[float] = None
