from typing import List

from domain.application.strategies.embedding.semantic_router import SemanticRouter
from domain.entities.classification import Classification
from domain.entities.route_result import RouteResult
from domain.interfaces import IPipeline, ITagger


class SemanticRoutingPipeline(IPipeline):
    """
    Pipeline that uses SemanticRouter to route queries based on semantic similarity.
    If no suitable anchor is found, it falls back to an LLM-based evaluation."""
    def __init__(self, router: SemanticRouter, tagger: ITagger, classification: Classification, tags: List[str], route_result: RouteResult, metadata: dict, **kwargs):
        self.router = router
        self.tagger = tagger
        self.classification = classification
        self.tags = tags
        self.route_result = route_result
        self.metadata = metadata
        self.kwargs = kwargs
