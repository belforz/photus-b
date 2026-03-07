from typing import Dict, List

import spacy

class SpacyAdapter:
    def __init__(self, model_name: str = "pt_core_news_md"):
        self.nlp = spacy.load(model_name)
        
    def extract_entities(self, text: str) -> List[Dict[str, str]]:
        doc = self.nlp(text)
        return [{"text": ent.text, "label": ent.label_} for ent in doc.ents]
    
    def extract_batchs_entities(self, list_of_texts: List[str], batch_size: int = 50) -> List[List[str]]:
        results = []
        for doc in self.nlp.pipe(list_of_texts, batch_size=batch_size):
            entities_from_texts = [ent.text for ent in doc.ents]
            results.append(entities_from_texts)
        return results
    