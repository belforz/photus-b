from typing import Dict, List
import spacy
from domain.entities.text_input import TextInput
from shared.exceptions import ModelNotFoundError
from shared.utils import logger
from domain.entities.tag import Tag
from domain.interfaces import ITagger



class SpacyAdapter(ITagger):
    def __init__(self, model_name: str = "pt_core_news_md"):
        try:
            self.nlp = spacy.load(model_name)
        except OSError as e:
            raise ModelNotFoundError(model_name) from e
        
    def tag_current_input(self, text_input: TextInput) -> List[Tag]:
        """
        Using Spacy to extract entities and convert them to a tag entity"""
        doc = self.nlp(text_input)
        tags = []
        for ent in doc.ents:
            tag_entity = Tag(entity=ent.text, label=ent.label_, text=text_input)
            tags.append(tag_entity)
        return tags
    
    def tag_batchs_inputs(self, list_of_texts: List[TextInput], batch_size: int = 50) -> List[List[Tag]]:
        """
        Using batches to extract entities and convert them to a tag entity
        """
        
        results = []
        for doc in self.nlp.pipe(list_of_texts, batch_size=batch_size):
            entities_from_texts = [ent.text for ent in doc.ents]
            results.append(entities_from_texts)
        return results
    