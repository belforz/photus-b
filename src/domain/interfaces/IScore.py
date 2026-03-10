from abc import ABC, abstractmethod
import abc
from domain.entities.text_input import TextInput
from src.domain.entities import Sentiment, Score




class IScorer(ABC):
    @abstractmethod
    def score(self, text: TextInput) -> Score:
        """
        Analyzes the given Sentiment object and returns a float number
        containing tags and sentiment analysis.
        
        Args: 
            sentiment: object
        
        Returns:
            score: object
        """
        raise NotImplementedError
        
