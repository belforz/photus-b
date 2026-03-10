from dataclasses import dataclass
from typing import List, Optional

from domain.entities.score import ScoreMetric
from domain.entities.text_input import TextInput


@dataclass(frozen=True)
class Sentiment:
    """Represents the complete sentiment analysis for a text."""

    score: ScoreMetric
    label: str  # e.g., "Positive", "Negative", "Neutral"
    text_input: Optional[TextInput] = str
    emotion: Optional[str] = None  # e.g., "Joy", "Anger", "Surprise"
    cosine_similarity: Optional[float] = None

    
