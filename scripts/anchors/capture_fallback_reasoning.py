#!/usr/bin/env python3
"""Chama call_semantic_fallback com Mistral real pra um ou mais textos e imprime
a ancora escolhida + o campo `reasoning` que o Mistral devolveu.

Complementar a validate_fallback_live.py (que roda os 46 casos padrao e ja grava
`fallback_reasoning` no JSON de saida): use este script pra inspecionar rapido o
raciocinio do Mistral num caso especifico, sem rodar a suite inteira.

Uso:
    python scripts/anchors/capture_fallback_reasoning.py "texto 1" "texto 2" ...

Sem argumentos, roda os 9 casos que mudaram de resultado na comparacao
prompt-antigo-vs-novo (ver docs/COMPARACAO_PROMPT_FALLBACK_REGRAS_FRONTEIRA.md):
7 resgatados + 1 regressao + 1 caso ainda instavel (nostalgia/ambiguo).
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "src"))

from domain.application.use_cases.categorize_text import CategorizationService  # noqa: E402

ANCHORS_PATH = os.path.join(ROOT, "data", "raw", "knowledge_anchors.json")

DEFAULT_CASES = [
    "pessoa lendo sem posar",
    "sobrecarga sensorial, nada no lugar",
    "grão de filme genuíno em retrato quase preto e branco",
    "atleta com expressão de dor extrema no rosto",
    "multidão animada mas com clima positivo, sem tensão",
    "pessoa em roupa profissional mas em ambiente real, não estúdio",
    "rosto pequeno e dividido em meio a uma multidão",
    "olhos fechados, luz de contorno, mão tocando o queixo",  # regressao (prompt novo errou)
    "estética vintage só que digitalmente perfeita, sem grão real",  # instavel entre Nostalgia/AMBIGUO
]


def main():
    texts = sys.argv[1:] or DEFAULT_CASES
    svc = CategorizationService(anchors_path=ANCHORS_PATH, enable_mistral_fallback=True)

    out = []
    for text in texts:
        embedding = svc._embedder.generate_embeddings(texts=text)
        ranked = svc.rank_anchors(embedding)
        result = svc.call_semantic_fallback(text, ranked)
        parsed = result.get("parsed") if result else None
        anchor = parsed.get("anchor") if parsed else None
        reasoning = parsed.get("reasoning") if parsed else None
        out.append({"text": text, "anchor_raw": anchor, "reasoning": reasoning})
        print(f"- {text!r}\n  anchor={anchor!r}\n  reasoning={reasoning!r}\n")

    out_path = os.path.join(ROOT, "data", "processed", "fallback_live_validation_reasoning.json")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f"Resultados salvos em: {out_path}")


if __name__ == "__main__":
    main()
