from typing import List, Optional

from pydantic import BaseModel, Field


class CategorizeRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Frase do usuário a ser categorizada")


class MatchSchema(BaseModel):
    anchor_id: str
    anchor_phrase: str
    score: float


class CategorizeResponse(BaseModel):
    input_text: str
    category: str
    category_code: str
    confidence: float
    technical: bool
    technical_score: float
    threshold: float
    low_confidence: bool
    confidence_threshold: float
    top_matches: List[MatchSchema]
    mistral_response: Optional[str] = None
    used_fallback: Optional[bool] = None
    sbert_anchor_before_fallback: Optional[str] = None
    fallback_reasoning: Optional[str] = None
    technical_null_reason: Optional[str] = None
