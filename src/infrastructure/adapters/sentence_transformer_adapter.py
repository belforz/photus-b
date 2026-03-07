from typing import List, Union

from sentence_transformers import SentenceTransformer
import numpy as np

class SentenceTransformerAdapter:
    def __init__(self, model_name: str = 'sentence-transformers/paraphrase-multilingual-mpnet-base-v2', prompt: str = ''):
        self._model = SentenceTransformer(model_name)
        self.prompt = prompt
    
    def generate_embeddings(self, texts: Union[str, List[str]]) -> np.ndarray:
        if isinstance(texts, str):
            texts = [texts]
        embeddings = self._model.encode(texts, convert_to_numpy=True)
        return embeddings
    
    
        
    
        