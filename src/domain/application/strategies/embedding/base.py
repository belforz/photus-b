from abc import ABC, abstractmethod
from typing import List


class IEmbedder(ABC):
    @abstractmethod
    def embed(self, text: str) -> List[float]:
        """
        Generates a dense vector representation of the given text.

        Args:
            text: Raw string to embed.

        Returns:
            List[float]: Fixed-length embedding vector.
        """
        raise NotImplementedError

    @abstractmethod
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generates embeddings for a list of texts.

        Args:
            texts: List of raw strings to embed.

        Returns:
            List[List[float]]: One embedding vector per input text.
        """
        raise NotImplementedError
