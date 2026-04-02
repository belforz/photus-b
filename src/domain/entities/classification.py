from dataclasses import dataclass, field
from typing import List, Optional

from src.domain.entities.sentiment import Sentiment
from src.domain.entities.tag import Tag
from src.domain.entities.text_input import TextInput
from src.domain.entities.route_result import RouteResult


@dataclass()
class Classification:
    """
    Aggregate root of the Photus-B NLP pipeline.

    Consolidates all analysis results for a single user input before
    the payload is sent to Photus-A.

    Attributes:
        input_text: The original user input.
        tags: Visual entities extracted by spaCy (e.g. "pessoa", "praia").
        route: Closest semantic anchor matched by the SemanticRouter.
        sentiment: Emotional classification from BERTimbau (optional stage).
    """

    input_text: TextInput
    tags: List[Tag] = field(default_factory=list)
    route: Optional[RouteResult] = None
    sentiment: Optional[Sentiment] = None
