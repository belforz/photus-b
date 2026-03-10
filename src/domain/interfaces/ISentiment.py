from abc import ABC, abstractmethod
import abc
from domain.entities.sentiment import Sentiment
from src.domain.entities import Classification, TextInput

class ISentimentRules(ABC):
    @abstractmethod
    def analyze_sentiments(self, text_input: TextInput) -> Sentiment:
        """
        Analyzes the given text input and returns a Sentiment score
        containing tags and sentiment analysis.
        
        Args: 
            text_input: object
        
        Returns: 
            Sentiment: object
            
        """
        raise NotImplementedError
    
    @abstractmethod
    def refine_sentiment(self, sentiment: Sentiment) -> Sentiment:
        
        """
        Re rank analysis if first atempt wasnt sure using S.BERT re rank classification
        
         Args: 
            text_input: object
        
        Returns: 
            Sentiment: object
            
        """
        raise NotImplementedError
        
        
        
    