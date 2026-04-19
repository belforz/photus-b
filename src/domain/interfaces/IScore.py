from abc import ABC, abstractmethod
import abc
from domain.entities.text_input import TextInput
from domain.entities import Score




class IScorer(ABC):
    @abstractmethod
    def score(self, text: TextInput) -> Score:
        """
        Analyzes the given TextInput object and returns a Score object
        containing tags and sentiment analysis.
        
        Args: 
            sentiment: object
        
        Returns:
            score: object
        """
        raise NotImplementedError
        
