from typing import List

from src.domain.application.strategies.embedding.base import IEmbedder
from src.infrastructure.adapters.sentence_transformer_adapter import SentenceTransformerAdapter


class SBERTEmbedder(IEmbedder):
    """IEmbedder implementation backed by SentenceTransformerAdapter.

    Converts numpy arrays to List[float]
    """

    def __init__(self, model_name: str = "paraphrase-multilingual-MiniLM-L12-v2") -> None:
        self._adapter = SentenceTransformerAdapter(model_name=model_name)

    def embed(self, text: str) -> List[float]:
        vector = self._adapter.generate_embeddings(text)
        return vector.tolist()

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        vectors = self._adapter.generate_embeddings(texts)
        return vectors.tolist()