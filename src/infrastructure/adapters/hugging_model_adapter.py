# for future use of BERTIMBAU from neuralmind https://huggingface.co/neuralmind/bert-base-portuguese-cased

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

class HuggingFaceAdapter:
    def __init__(self, model_id: str = "neuralmind/bert-base-portuguese-cased"):
        self.model_id = model_id
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self._tokenizer = AutoTokenizer.from_pretrained(model_id)
        self._model = AutoModelForCausalLM.from_pretrained(model_id).to(self.device)
        
    def _encode(self, text:str):
        return self._tokenizer(text, return_tensors="pt").to(self.device)
    
    def _decode(self, tokens) -> str:
        return self._tokenizer.decode(tokens, skip_special_tokens=True)
    
    def generate(self, prompt: str, **kwargs) -> str:
        inputs = self._encode(prompt)
        with torch.no_grad():
            output_tokens = self._model.generate(**inputs, pad_token_id=self._tokenizer.eos_token_id, **kwargs)
        return self._decode(output_tokens)