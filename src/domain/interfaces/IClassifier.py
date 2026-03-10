from abc import ABC, abstractmethod
import abc
from src.domain.entities import Classification, TextInput

class IClassifier(ABC):
    @abstractmethod
    def classify(self, text_input: TextInput) -> Classification:
        """
        Analyzes the given text input and returns a Classification entity
        containing tags and sentiment analysis.
        
        Args: 
            text_input: object
        
        Returns:
            Classification: object
        """
        raise NotImplementedError
        
