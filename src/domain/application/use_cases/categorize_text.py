"""Categorize free-text input against the knowledge-anchor graph.

Shared by the CLI tooling (scripts/anchors/run_custom_sentences.py) and the
presentation-layer API (src/presentation/api) so both entry points score
anchors and detect technical inputs the exact same way.
"""
import json
import math
import re
import unicodedata
from dataclasses import dataclass, field
from typing import Any, List, Optional

from infrastructure.adapters.mistral_adapter import MistralConnector
from infrastructure.adapters.sentence_transformer_adapter import SentenceTransformerAdapter
from infrastructure.config.prompts.loader import load_prompt
from shared.utils import logger

THRESHOLD_TECNICO = 0.48

_REGEX_PARAMETRO_PURO = re.compile(
    r"\b(f/\d[\d.]*|iso\s?\d{2,6}|\d+/\d+s?)\b",
    re.IGNORECASE,
)
_REGEX_PARENTHETICAL = re.compile(r"\s*\([^)]*\)")


def _cosine(a: list, b: list) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    return dot / (na * nb) if na and nb else 0.0


def _base_label(anchor_id: str) -> str:
    """Strip the descriptive parenthetical, e.g. 'Solenidade (Estase)' -> 'Solenidade'."""
    return _REGEX_PARENTHETICAL.sub("", anchor_id).strip()


def slugify_category(value: str) -> str:
    """Create a stable integration-friendly category code from an anchor label."""
    text = _base_label(value).lower()
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^a-z0-9]+", "_", text)
    return text.strip("_") or "unknown"


@dataclass
class CategoryMatch:
    anchor_id: str
    anchor_phrase: str
    score: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "anchor_id": self.anchor_id,
            "anchor_phrase": self.anchor_phrase,
            "score": self.score,
        }


@dataclass
class CategoryResult:
    input_text: str
    category: str
    category_code: str
    confidence: float
    technical: bool
    technical_score: float
    threshold: float
    top_matches: List[CategoryMatch] = field(default_factory=list)
    mistral_response: Optional[str] = None

    def to_category_payload(self) -> dict[str, Any]:
        """Minimal payload shape consumed by downstream systems (Photus A)."""
        return {
            "input_text": self.input_text,
            "category": self.category,
            "category_code": self.category_code,
            "confidence": self.confidence,
            "technical": self.technical,
            "technical_score": self.technical_score,
            "threshold": self.threshold,
        }

    def to_dict(self) -> dict[str, Any]:
        payload = self.to_category_payload()
        payload["top_matches"] = [m.to_dict() for m in self.top_matches]
        payload["mistral_response"] = self.mistral_response
        return payload


class CategorizationService:
    """Loads anchors + the embedding model once and classifies free-text into a category.

    Mistral is only used as a fallback for technical inputs and is instantiated
    lazily (and optionally), since MISTRAL_API_KEY may not be configured in
    every environment.
    """

    def __init__(
        self,
        anchors_path: str,
        embedder: Optional[SentenceTransformerAdapter] = None,
        enable_mistral_fallback: bool = True,
    ):
        self._anchors = self._load_anchors(anchors_path)
        self._embedder = embedder or SentenceTransformerAdapter()
        self._enable_mistral_fallback = enable_mistral_fallback
        self._mistral: Optional[MistralConnector] = None

    @staticmethod
    def _load_anchors(path: str) -> dict:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _mistral_connector(self) -> Optional[MistralConnector]:
        if not self._enable_mistral_fallback:
            return None
        if self._mistral is None:
            try:
                self._mistral = MistralConnector()
            except ValueError:
                logger.warning(
                    "MISTRAL_API_KEY not configured; disabling technical fallback."
                )
                self._enable_mistral_fallback = False
                return None
        return self._mistral

    def rank_anchors(self, embedding) -> List[CategoryMatch]:
        """Return anchors deduplicated by anchor_id, sorted by best cosine score."""
        best: dict[str, CategoryMatch] = {}
        for aid, phrase, aemb in zip(
            self._anchors.get("anchors_ids", []),
            self._anchors.get("phrases", []),
            self._anchors.get("embeddings", []),
        ):
            score = float(_cosine(embedding, aemb))
            if aid not in best or score > best[aid].score:
                best[aid] = CategoryMatch(anchor_id=aid, anchor_phrase=phrase, score=score)
        return sorted(best.values(), key=lambda m: m.score, reverse=True)

    def _is_technical(self, text: str, ranked: List[CategoryMatch]) -> tuple[bool, float]:
        if _REGEX_PARAMETRO_PURO.search(text):
            return True, 1.0
        score_tecnico = next(
            (m.score for m in ranked if m.anchor_id == "__tecnico__"), 0.0
        )
        return score_tecnico >= THRESHOLD_TECNICO, score_tecnico

    def call_mistral_technical(self, text: str) -> Optional[str]:
        """Send a technical input to Mistral using the technical system prompt."""
        connector = self._mistral_connector()
        if connector is None:
            return None
        try:
            system_prompt = load_prompt("base")
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text},
            ]
            response = connector.send_message(messages, temperature=0.1)
            if isinstance(response, list):
                response = "".join(
                    chunk.text for chunk in response if hasattr(chunk, "text")
                )
            if response is None:
                logger.warning("Mistral returned None response for text: %s", text)
                return None
            return str(response)
        except Exception as e:
            logger.error("Mistral request failed: %s", e, exc_info=True)
            return None

    def categorize(
        self, text: str, top_k: int = 5, route_technical_to_mistral: bool = True
    ) -> CategoryResult:
        if not text or not text.strip():
            raise ValueError("text must not be empty")

        embedding = self._embedder.generate_embeddings(texts=text)
        ranked = self.rank_anchors(embedding)
        technical, tech_score = self._is_technical(text, ranked)

        mistral_response = None
        if technical and route_technical_to_mistral:
            mistral_response = self.call_mistral_technical(text)

        best = ranked[0] if ranked else CategoryMatch("unknown", "", 0.0)
        return CategoryResult(
            input_text=text,
            category=_base_label(best.anchor_id),
            category_code=slugify_category(best.anchor_id),
            confidence=best.score,
            technical=technical,
            technical_score=float(tech_score),
            threshold=THRESHOLD_TECNICO,
            top_matches=ranked[:top_k],
            mistral_response=mistral_response,
        )
