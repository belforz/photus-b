#!/usr/bin/env python3
"""Validacao real (nao simulada) do fallback score/gap -> LLM conector.

Roda os 46 casos de roteamento semantico (Grupo A + B) do diagnostico original
contra o CategorizationService real, com route_technical_to_llm=True -
ou seja, toda vez que score/gap dispararem a regra, o LLM conector e chamado de
verdade. Reporta pra cada caso: resultado sem fallback (SBERT puro), se o
fallback disparou, o que o LLM conector respondeu, o resultado final, e se bateu
com a ancora esperada.

Nao edita nenhuma ancora. So exercita o codigo real de categorize_text.py.
"""
import json
import os
import re
import sys
import time
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))

from domain.application.use_cases.categorize_text import (  # noqa: E402
    CategorizationService,
    THRESHOLD_SCORE_FALLBACK,
    THRESHOLD_GAP_FALLBACK,
)
from infrastructure.config.settings import settings  # noqa: E402

ANCHORS_PATH = os.path.join(ROOT, "data", "raw", "knowledge_anchors.json")

GROUP_A = {
    "Vitalidade (Ação)": [
        "atleta no ápice do salto sob sol forte",
        "corrida com respingos de água",
        "energia explosiva ao meio-dia",
    ],
    "Solenidade (Estase)": [
        "produto isolado em fundo branco",
        "ambiente minimalista vazio e simétrico",
        "silêncio visual, nada em movimento",
    ],
    "Conexão (Close-up)": [
        "olhos fechados, luz de contorno, mão tocando o queixo",
        "rosto ocupando o quadro, olhar direto",
        "abraço com rostos próximos em foco",
    ],
    "Distanciamento (Low-key)": [
        "poste de luz solitário contra escuridão quase total",
        "corredor vazio e escuro",
        "silhueta isolada, ninguém por perto",
    ],
    "Simplicidade (Cotidiano)": [
        "cozinha iluminada por luz de janela, sem produção",
        "pessoa lendo sem posar",
        "cena doméstica comum sem drama",
    ],
    "Conflito (Caos)": [
        "multidão densa vista de cima",
        "rua com grafite e detritos, tensão visual",
        "sobrecarga sensorial, nada no lugar",
    ],
    "Nostalgia (Analógico)": [
        "grão de filme genuíno em retrato quase preto e branco",
        "textura de negativo Kodak, tira de contato",
        "estética vintage de décadas passadas",
    ],
    "Sublime (Paisagem)": [
        "pessoa minúscula de costas contra paisagem grandiosa",
        "oceano sem fim, céu épico",
        "montanha ao pôr do sol dramático",
    ],
    "Corporativo (Focado)": [
        "headshot com fundo neutro de estúdio",
        "iluminação de estúdio limpa, roupa formal",
        "foto que colocaria no LinkedIn sem hesitar",
    ],
    "Noturno (Festa)": [
        "pista de dança com luzes neon e grupo animado",
        "show com multidão eufórica",
        "brinde entre amigos à noite",
    ],
}

GROUP_B = [
    ("show de rock em ambiente escuro", "Noturno (Festa)"),
    ("atleta com expressão de dor extrema no rosto", "Conflito (Caos)"),
    ("cena estática mas com rosto próximo e emocional", "Conexão (Close-up)"),
    ("montanha grandiosa fotografada à noite", "Sublime (Paisagem)"),
    ("ambiente escuro mas festivo e animado", "Noturno (Festa)"),
    ("cena doméstica mas visivelmente produzida e estilizada", "Solenidade (Estase)"),
    ("multidão animada mas com clima positivo, sem tensão", "Vitalidade (Ação)"),
    ("ambiente noturno só que festivo, não tenso", "Noturno (Festa)"),
    ("estética vintage só que digitalmente perfeita, sem grão real", "AMBIGUO/DESCARTE"),
    ("cena antiga mas grandiosa, tipo paisagem histórica", "Sublime (Paisagem)"),
    ("paisagem grandiosa mas fotografada no escuro", "Distanciamento (Low-key)"),
    ("retrato próximo e emotivo em ambiente de estúdio formal", "Conexão (Close-up)"),
    ("pessoa em roupa profissional mas em ambiente real, não estúdio", "Simplicidade (Cotidiano)"),
    ("cena social mas estática e formal, tipo coquetel corporativo", "Corporativo (Focado)"),
    ("rosto pequeno e dividido em meio a uma multidão", "Conflito (Caos)"),
    ("pessoa sozinha ao entardecer, sombras longas", "NAO_DISTANCIAMENTO(horario_errado)"),
]


def main():
    print(f"THRESHOLD_SCORE_FALLBACK={THRESHOLD_SCORE_FALLBACK}  THRESHOLD_GAP_FALLBACK={THRESHOLD_GAP_FALLBACK}\n")
    print("Carregando servico com LLM real (enable_llm_fallback=True)...")
    svc = CategorizationService(anchors_path=ANCHORS_PATH, enable_mistral_fallback=True)

    cases = []
    for expected, texts in GROUP_A.items():
        for t in texts:
            cases.append(("A", t, expected))
    for t, expected in GROUP_B:
        cases.append(("B", t, expected))

    print(f"{len(cases)} casos totais\n")

    rows = []
    mistral_calls = 0
    t_start = time.time()

    for i, (group, text, expected) in enumerate(cases, 1):
        r_sbert_only = svc.categorize(text, top_k=3, route_technical_to_mistral=False)
        sbert_correct = r_sbert_only.category == expected.split(" (")[0] if "(" not in expected else (
            r_sbert_only.category == expected.split(" (")[0]
        )
        # compara pelo anchor_id completo do top1 (mais preciso que category, que ja perdeu o parenteses)
        sbert_top1_anchor = r_sbert_only.top_matches[0].anchor_id if r_sbert_only.top_matches else None
        sbert_correct = sbert_top1_anchor == expected

        r_live = svc.categorize(text, top_k=3, route_technical_to_mistral=True)
        if r_live.used_fallback:
            mistral_calls += 1
        final_anchor = None
        for m in r_live.top_matches:
            if _base_label_match(m, r_live.category):
                final_anchor = m.anchor_id
                break
        # categoria final e o label sem parenteses; reconstitui o anchor_id completo via category+category_code nao e trivial,
        # entao usamos sbert_anchor_before_fallback + used_fallback pra deduzir, e comparamos por _base_label
        expected_base = expected.split(" (")[0]
        final_correct = r_live.category == expected_base

        rows.append({
            "group": group,
            "text": text,
            "expected": expected,
            "sbert_only_anchor": sbert_top1_anchor,
            "sbert_only_score": r_sbert_only.top_matches[0].score if r_sbert_only.top_matches else None,
            "sbert_correct": sbert_correct,
            "used_fallback": r_live.used_fallback,
            "sbert_anchor_before_fallback": r_live.sbert_anchor_before_fallback,
            "fallback_reasoning": r_live.fallback_reasoning,
            "final_category": r_live.category,
            "final_confidence": r_live.confidence,
            "final_correct": final_correct,
        })
        print(f"[{i}/{len(cases)}] {text[:55]:<55} sbert={sbert_top1_anchor!r:<28} fallback={r_live.used_fallback} final={r_live.category!r} correct={final_correct}")

    elapsed = time.time() - t_start
    print(f"\nTempo total: {elapsed:.1f}s | chamadas ao Mistral (fallback disparado): {mistral_calls}")

    model_slug = re.sub(r"[^a-zA-Z0-9]+", "-", settings.LLM_MODEL_CURRENT_NAME).strip("-")
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    out_path = os.path.join(
        ROOT, "data", "processed", f"fallback_live_validation__{model_slug}__{timestamp}.json"
    )
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({
            "model": settings.LLM_MODEL_CURRENT_NAME,
            "timestamp": timestamp,
            "threshold_score_fallback": THRESHOLD_SCORE_FALLBACK,
            "threshold_gap_fallback": THRESHOLD_GAP_FALLBACK,
            "total_cases": len(cases),
            "mistral_calls": mistral_calls,
            "elapsed_seconds": elapsed,
            "rows": rows,
        }, f, ensure_ascii=False, indent=2)
    print(f"Resultados salvos em: {out_path}")


def _base_label_match(m, category_label):
    import re
    base = re.sub(r"\s*\([^)]*\)", "", m.anchor_id).strip()
    return base == category_label


if __name__ == "__main__":
    main()
