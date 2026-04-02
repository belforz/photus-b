from abc import ABC, abstractmethod
from typing import Callable

from domain.entities.classification import Classification
from domain.entities.text_input import TextInput


Stage = Callable[[Classification], Classification]


class IPipeline(ABC):
    """
    Interface for a base pipeline that can be extended to implement specific processing logic.
    """
    @abstractmethod
    def process(self, input_data:TextInput) -> Classification:
        """
        Process the input data and return a Classification entity.

        Args:
            input_data (TextInput): The raw text input to be processed.
        Returns:
            Classification: The result of processing the input, containing tags, sentiment, etc.
        """        
        raise NotImplementedError
    
    @abstractmethod
    def add_stage(self, stage: Stage) -> None:
        """
        Add a processing stage to the pipeline.

        Args:
            stage: A callable that takes a Classification and returns a modified Classification.
        """
        raise NotImplementedError
    
    @abstractmethod
    def clear_stage(self) -> None:
        """
        Clear processing stages from the pipeline.
        """
        raise NotImplementedError
    
    