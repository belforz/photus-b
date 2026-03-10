from abc import ABC, abstractmethod
import abc
from typing import List
from domain.entities.sentiment import Sentiment
from domain.entities.tag import Tag
from src.domain.entities import Classification, TextInput

class ITagger(ABC):
    @abstractmethod
    def tag_current_input(self, text_input: TextInput) -> List[Tag]:
        """
        Analyzes the given text input to separate entities and labels.
        
        Args: 
            text_input: object
        
        Returns:
            list: Tags
        """
        raise NotImplementedError
    
    def tag_batchs_inputs(self, list_of_texts: List[str], batch_size: int = 50) -> List[Tag]:
        """
        Analyzes the given text input to separate entities and labels.
        
        Args: 
            text_input: object
        
        Returns:
            list: Tags
        """
        raise NotImplementedError
        
        