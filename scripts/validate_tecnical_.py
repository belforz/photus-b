#!/usr/bin/env python3

import sys; sys.path.insert(0,'src')
from domain.application.use_cases.categorize_text import CategorizationService

FRASES_ANCORAS_TESTSET = [
    "f/1.4, ISO 3200, ambiente completamente escuro, só uma silhueta na porta, sozinha",
    "abertura máxima f/1.2 pra desfocar tudo, só o olho com catchlight nítido, bem de perto",
    "compensação de exposição negativa de dois stops pra deixar a cena bem escura, com a pessoa sozinha e isolada no quadro",
    "bracketing de exposição em três quadros pra capturar o dynamic range da montanha ao amanhecer",
    "push processing pra +2 stops no filme, deixando o grão mais aparente, tipo uma foto tirada há décadas",
    "softbox a 45 graus e reflector de preenchimento pro retrato de LinkedIn",
    "flash com sincronização lenta pra borrar as luzes da pista de dança e congelar o grupo dançando",
    "ajusta o negativo pra ficar mais cru"
    
]


def main():
    svc = CategorizationService(anchors_path='data/raw/knowledge_anchors.json')

    for text in FRASES_ANCORAS_TESTSET:
     print('='*80)
     print('TEXTO:', text)
     r = svc.categorize(text)
     print('technical:', r.technical, '| category:', r.category)
     print(
    f"mistral_response: {r.mistral_response}\n"
    f"used_fallback: {r.used_fallback}\n"
    f"sbert_anchor_before_fallback: {r.sbert_anchor_before_fallback}\n"
    f"fallback_reasoning: {r.fallback_reasoning}\n"
    f"technical_null_reason: {r.technical_null_reason}"
)

     
    
if __name__ == "__main__":
    main()

