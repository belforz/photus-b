from typing import List, Union

from sentence_transformers import SentenceTransformer
import numpy as np

class SentenceTransformerAdapter:
    def __init__(self, model_name: str = 'paraphrase-multilingual-MiniLM-L12-v2'):
        self._model = SentenceTransformer(model_name)
    
    def generate_embeddings(self, texts: Union[str, List[str]]) -> Union[np.ndarray, List[float]]:
        """ Generate embeddings for a single text or a list of texts

        Args:
            texts (Union[str, List[str]]): _description_
        
        Returns:
            Union[np.ndarray, List[float]]: _description_
        
        """
        is_single_string = isinstance(texts, str)
        if is_single_string:
            texts = [texts]
        embeddings = self._model.encode(texts, convert_to_numpy=True)
        if is_single_string:
            return embeddings[0]
        return embeddings
    
    
        
    
        