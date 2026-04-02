from dataclasses import dataclass


@dataclass(frozen=True)
class RouteResult:
    """Represents the output of the SemanticRouter.

    Maps a user text input to the closest knowledge anchor
    and the cosine similarity score that justified the match.

    Attributes:
        anchor_id: Human-readable ID of the matched anchor (e.g. "Vitalidade (Ação)").
        score: Cosine similarity between the input embedding and the anchor vector.
    """

    anchor_id: str
    score: float
