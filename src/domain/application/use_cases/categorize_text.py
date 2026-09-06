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
"""Score mínimo contra a âncora `__tecnico__` para considerar o input um pedido técnico."""

CONFIDENCE_THRESHOLD_LOW = 0.45
"""Abaixo disso, a categoria vencedora é considerada pouco confiável (`low_confidence=True`)."""

THRESHOLD_SCORE_FALLBACK = 0.63
"""Score mínimo do top1 semântico abaixo do qual desviamos pro Mistral em vez de confiar nele.

Calibrado empiricamente (não é o `top_score >= 0.55` da seção 3.1 da memória oficial, que nunca
foi implementado nem calibrado) — ver `docs/CALIBRACAO_THRESHOLD_MISTRAL.md`.
"""

THRESHOLD_GAP_FALLBACK = 0.04
"""Gap mínimo entre top1 e top2 abaixo do qual desviamos pro Mistral, mesmo com score alto.

Calibrado empiricamente junto com `THRESHOLD_SCORE_FALLBACK` — ver
`docs/CALIBRACAO_THRESHOLD_MISTRAL.md`.
"""

_REGEX_PARAMETRO_PURO = re.compile(
    r"\b(f/\d[\d.]*|iso\s?\d{2,6}|\d+/\d+s?)\b",
    re.IGNORECASE,
)
_REGEX_PARENTHETICAL = re.compile(r"\s*\([^)]*\)")
_REGEX_JSON_FENCE = re.compile(r"```(?:json)?\s*(.*?)\s*```", re.DOTALL)


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


def _parse_json_object(text: str) -> Optional[dict]:
    """Best-effort parse of a JSON object out of a Mistral response (handles ```json fences)."""
    candidate = text.strip()
    fence_match = _REGEX_JSON_FENCE.search(candidate)
    if fence_match:
        candidate = fence_match.group(1).strip()
    try:
        parsed = json.loads(candidate)
        return parsed if isinstance(parsed, dict) else None
    except (json.JSONDecodeError, TypeError):
        return None


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
    low_confidence: bool = False
    confidence_threshold: float = CONFIDENCE_THRESHOLD_LOW
    top_matches: List[CategoryMatch] = field(default_factory=list)
    mistral_response: Optional[str] = None
    used_fallback: bool = False
    """True se score/gap do top1 semântico ficaram abaixo do calibrado e o Mistral decidiu a âncora."""
    sbert_anchor_before_fallback: Optional[str] = None
    """Âncora que o SBERT tinha escolhido antes do desvio pro Mistral (só preenchido se `used_fallback=True`), pra auditoria/debug."""

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
            "low_confidence": self.low_confidence,
            "confidence_threshold": self.confidence_threshold,
            "used_fallback": self.used_fallback,
            "sbert_anchor_before_fallback": self.sbert_anchor_before_fallback,
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
        ranked = sorted(best.values(), key=lambda m: m.score, reverse=True)
        logger.info(
            "[step 2/4] ranked {} unique anchors; top-5: {}",
            len(ranked),
            ", ".join(f"{m.anchor_id}={m.score:.3f}" for m in ranked[:5]),
        )
        return ranked

    def _is_technical(self, text: str, ranked: List[CategoryMatch]) -> tuple[bool, float]:
        regex_match = _REGEX_PARAMETRO_PURO.search(text)
        if regex_match:
            logger.info(
                "[step 3/4] technical=True via regex match {!r} (bypasses threshold={})",
                regex_match.group(0),
                THRESHOLD_TECNICO,
            )
            return True, 1.0

        score_tecnico = next(
            (m.score for m in ranked if m.anchor_id == "__tecnico__"), 0.0
        )
        technical = score_tecnico >= THRESHOLD_TECNICO
        logger.info(
            "[step 3/4] technical check: __tecnico__ score={:.3f} vs threshold={} -> technical={}",
            score_tecnico,
            THRESHOLD_TECNICO,
            technical,
        )
        return technical, score_tecnico

    def call_mistral_technical(self, text: str) -> Optional[str]:
        """Send a technical input to Mistral using the technical system prompt."""
        connector = self._mistral_connector()
        if connector is None:
            logger.warning("[step 4/4] Mistral fallback unavailable; skipping.")
            return None
        try:
            logger.info("[step 4/4] routing technical input to Mistral...")
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
                logger.warning(f"[step 4/4] Mistral returned None response for text: {text!r}")
                return None
            logger.info(f"[step 4/4] Mistral responded ({len(str(response))} chars)")
            return str(response)
        except Exception as e:
            logger.error(f"[step 4/4] Mistral request failed: {e}", exc_info=True)
            return None

    def _resolve_anchor_label(self, name: Any, ranked: List[CategoryMatch]) -> Optional[CategoryMatch]:
        """Match the free-text anchor name Mistral returned back to a ranked CategoryMatch.

        Compares case-insensitively against both the full anchor_id (e.g. "Vitalidade (Ação)")
        and its base label without the parenthetical (e.g. "Vitalidade"), and skips `__tecnico__`
        since this fallback only runs on the non-technical branch.
        """
        if not isinstance(name, str) or not name.strip():
            return None
        needle = name.strip().lower()
        for m in ranked:
            if m.anchor_id == "__tecnico__":
                continue
            if needle == m.anchor_id.lower() or needle == _base_label(m.anchor_id).lower():
                return m
        return None

    def call_semantic_fallback(self, text: str, ranked: List[CategoryMatch]) -> Optional[dict]:
        """Ask Mistral to pick an anchor when the SBERT top1 is low-score or the gap to top2 is small.

        Uses the `fallback` prompt (lists the 10 semantic anchors + JSON schema with an `anchor`
        field), reusing the same lazily-instantiated Mistral connector as the technical fallback.
        """
        connector = self._mistral_connector()
        if connector is None:
            logger.warning("[fallback] Mistral unavailable; keeping SBERT top1.")
            return None
        try:
            logger.info("[fallback] score/gap below calibrated threshold, asking Mistral to pick the anchor...")
            system_prompt = load_prompt("fallback")
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text},
            ]
            response = connector.send_message(messages, temperature=0.1)
            if response is None:
                logger.warning(f"[fallback] Mistral returned None response for text: {text!r}")
                return None
            parsed = _parse_json_object(str(response))
            if parsed is None:
                logger.warning(f"[fallback] could not parse Mistral JSON response: {response!r}")
                return None
            matched = self._resolve_anchor_label(parsed.get("anchor"), ranked)
            logger.info(
                "[fallback] Mistral picked anchor={!r} -> resolved={}",
                parsed.get("anchor"),
                matched.anchor_id if matched else None,
            )
            return {"raw": str(response), "parsed": parsed, "match": matched}
        except Exception as e:
            logger.error(f"[fallback] Mistral request failed: {e}", exc_info=True)
            return None

    def categorize(
        self, text: str, top_k: int = 5, route_technical_to_mistral: bool = True
    ) -> CategoryResult:
        if not text or not text.strip():
            raise ValueError("text must not be empty")

        logger.info(f"[step 1/4] categorizing text={text!r} (len={len(text)})")

        embedding = self._embedder.generate_embeddings(texts=text)
        logger.debug(f"[step 1/4] embedding generated (dim={len(embedding)})")

        ranked = self.rank_anchors(embedding)
        technical, tech_score = self._is_technical(text, ranked)

        mistral_response = None
        if technical and route_technical_to_mistral:
            mistral_response = self.call_mistral_technical(text)

        best = ranked[0] if ranked else CategoryMatch("unknown", "", 0.0)
        second = ranked[1] if len(ranked) > 1 else None
        gap = (best.score - second.score) if second else None

        low_confidence = best.score < CONFIDENCE_THRESHOLD_LOW
        if low_confidence:
            logger.warning(
                "[step 4/4] low confidence: best match {} score={:.3f} < threshold={}",
                best.anchor_id,
                best.score,
                CONFIDENCE_THRESHOLD_LOW,
            )
        else:
            logger.info(
                "[step 4/4] result: category={} confidence={:.3f} (>= threshold={})",
                _base_label(best.anchor_id),
                best.score,
                CONFIDENCE_THRESHOLD_LOW,
            )

        final_match = best
        final_confidence = best.score
        used_fallback = False
        sbert_anchor_before_fallback = None

        should_fallback = best.score < THRESHOLD_SCORE_FALLBACK or (
            gap is not None and gap < THRESHOLD_GAP_FALLBACK
        )
        if not technical and should_fallback and route_technical_to_mistral:
            logger.info(
                "[fallback] score={:.3f} gap={} below calibrated thresholds (score_min={}, gap_min={})",
                best.score,
                f"{gap:.3f}" if gap is not None else "n/a",
                THRESHOLD_SCORE_FALLBACK,
                THRESHOLD_GAP_FALLBACK,
            )
            sbert_anchor_before_fallback = best.anchor_id
            used_fallback = True
            fallback_result = self.call_semantic_fallback(text, ranked)
            match = fallback_result.get("match") if fallback_result else None
            if match is not None:
                final_match = match
                parsed_confidence = fallback_result["parsed"].get("confidence")
                final_confidence = (
                    float(parsed_confidence)
                    if isinstance(parsed_confidence, (int, float))
                    else match.score
                )
            else:
                logger.warning(
                    "[fallback] Mistral unavailable or unresolved; keeping SBERT top1 {}",
                    best.anchor_id,
                )

        return CategoryResult(
            input_text=text,
            category=_base_label(final_match.anchor_id),
            category_code=slugify_category(final_match.anchor_id),
            confidence=final_confidence,
            technical=technical,
            technical_score=float(tech_score),
            threshold=THRESHOLD_TECNICO,
            low_confidence=low_confidence,
            confidence_threshold=CONFIDENCE_THRESHOLD_LOW,
            top_matches=ranked[:top_k],
            mistral_response=mistral_response,
            used_fallback=used_fallback,
            sbert_anchor_before_fallback=sbert_anchor_before_fallback,
        )
