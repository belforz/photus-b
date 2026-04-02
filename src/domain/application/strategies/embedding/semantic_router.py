
import json
import os
import threading
from typing import List, Tuple

import numpy as np

from domain.application.strategies.embedding.base import IEmbedder
from domain.entities.route_result import RouteResult
from infrastructure.adapters.mistral_adapter import MistralConnector
from shared.utils import logger

class SemanticRouter:
    """Maps user inputs to the closest knowledge anchor based on cosine similarity.
    
     Features:
    - loads anchors from a JSON file with keys: metadata, anchors_ids, phrases, embeddings
    - computes representative anchor vectors (mean per anchor id)
    - exposes `route()` returning a `RouteResult` when the top score >= threshold
    - supports dynamic updates: add_anchor, remove_anchor, update_anchor, reload, save
    - thread-safe for updates
    
    
    """
    
    #1 - Load anchors from JSON, compute anchor vectors, and initialize adapter
    def __init__(self, embedder: IEmbedder, threshold: float = 0.65, anchors_path: str | None = None):
        self._embedder = embedder
        self._anchors_path = anchors_path
        self._threshold = threshold
        
        self._lock = threading.Lock()  # For thread-safe updates
        self._anchors_ids = List[str] = []
        self._phrases = List[str] = []
        self._embeddings = List[List[float]] = []
        if os.path.exists(anchors_path):
            self.load_from_json(anchors_path)
        else: 
            return None
        
        
    # LOADING AND SAVING ANCHORS
    def load_from_json(self, path: str) -> None:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    
    def save_to_json(self, path: str) -> None:
        path = path or self._anchors_path
        payload = {
            "metadata": {
                "model_name": self._embedder.model_name,
                "vector_dim": len(self._embeddings[0]) if self._embeddings else 0,
                "total_anchors": len(self._anchors_ids)
            },
            "anchors_ids": self._anchors_ids,
            "phrases": self._phrases,
            "embeddings": self._embeddings
        }
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
            
            
        #   I will not use yet, but this is how I would load the data and compute the anchor vectors:  
        # with self._lock:
        #     self._anchors_ids = data["anchors_ids"]
        #     self._phrases = data["phrases"]
        #     self._embeddings = data["embeddings"]
        #     self._compute_anchor_vectors()
            
    
    def get_top_k(self, query: str, k: int = 3) -> List[Tuple[str, float]]:
        """Returns the top-k closest anchors to the query, along with their cosine similarity scores."""
        query_vec = np.array(self._embedder.embed(query), dtype=float)
        norms = np.linalg.norm(self._embeddings, axis=1) * np.linalg.norm(query_vec)
        norms[norms == 0] = 1e-8 # normalization to avoid division by zero
        sims = (self._embeddings @ query_vec).squeeze() / norms
        pairs = list(zip(self._anchors_ids, sims))
        pairs.sort(key=lambda x: x[1], reverse=True)
        return pairs[:k]
        
        
    # Route input text to closest anchor
    def route(self, query: str, top_k: int = 1) -> RouteResult | None:
        top = self.get_top_k(query, k=top_k)
        if not top:
            logger.warning("SemanticRouter: No anchors available to route.")
            return None
        anchor_id, score = top[0]
        if score >= self._threshold:
            logger.info(f"SemanticRouter: Routed query '{query}' to anchor '{anchor_id}' with score {score:.3f}.")
            return RouteResult(anchor_id=anchor_id, score=score)
        else:
            logger.info(f"SemanticRouter: No anchor met the threshold for query '{query}'.")
            return None
        
    def fallback_to_llm(self, query: str) -> RouteResult:
        if self._threshold is None and RouteResult is None:
            logger.warning("SemanticRouter: No anchors available, falling back to LLM.")
            llm_connection = MistralConnector()
            response = llm_connection.send_message_in_portuguese(query)
            return RouteResult(anchor_id=response, score=response.find("anchor_id"))  # Dummy score based on response content
        else:
            logger.warning("SemanticRouter: Anchors are available, fallback to LLM is not needed.")
            return None
            
    
    
    
    
        
        
        