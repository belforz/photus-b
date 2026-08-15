#!/usr/bin/env python3
"""Diagnostico de saude das ancoras semanticas do Photus B.

Reaproveita CategorizationService (roteador em producao) para rodar uma
bateria de testes (grupos A/B/C) e salvar metricas brutas em JSON.
Nao altera nenhum arquivo de ancoras/thresholds do projeto.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))

from domain.application.use_cases.categorize_text import (  # noqa: E402
    CategorizationService,
    THRESHOLD_TECNICO,
    CONFIDENCE_THRESHOLD_LOW,
)

ANCHORS_PATH = os.path.join(ROOT, "data", "raw", "knowledge_anchors.json")

# ---------------------------------------------------------------------------
# GRUPO A - Casos centrais por ancora (deveriam rotear com score alto e gap grande)
# ---------------------------------------------------------------------------
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

# ---------------------------------------------------------------------------
# GRUPO B - Casos de fronteira / rejeicao documentados
# (texto, ancora_correta_esperada, armadilha)
# ---------------------------------------------------------------------------
GROUP_B = [
    ("show de rock em ambiente escuro", "Noturno (Festa)", "Vitalidade (Ação)"),
    ("atleta com expressão de dor extrema no rosto", "Conflito (Caos)", "Vitalidade (Ação)"),
    ("cena estática mas com rosto próximo e emocional", "Conexão (Close-up)", "Solenidade (Estase)"),
    ("montanha grandiosa fotografada à noite", "Sublime (Paisagem)", "Distanciamento (Low-key)"),
    ("ambiente escuro mas festivo e animado", "Noturno (Festa)", "Distanciamento (Low-key)"),
    ("cena doméstica mas visivelmente produzida e estilizada", "Solenidade (Estase)", "Simplicidade (Cotidiano)"),
    ("multidão animada mas com clima positivo, sem tensão", "Vitalidade (Ação)", "Conflito (Caos)"),
    ("ambiente noturno só que festivo, não tenso", "Noturno (Festa)", "Conflito (Caos)"),
    ("estética vintage só que digitalmente perfeita, sem grão real", "AMBIGUO/DESCARTE", "Nostalgia (Analógico)"),
    ("cena antiga mas grandiosa, tipo paisagem histórica", "Sublime (Paisagem)", "Nostalgia (Analógico)"),
    ("paisagem grandiosa mas fotografada no escuro", "Distanciamento (Low-key)", "Sublime (Paisagem)"),
    ("retrato próximo e emotivo em ambiente de estúdio formal", "Conexão (Close-up)", "Corporativo (Focado)"),
    ("pessoa em roupa profissional mas em ambiente real, não estúdio", "Simplicidade (Cotidiano)", "Corporativo (Focado)"),
    ("cena social mas estática e formal, tipo coquetel corporativo", "Corporativo (Focado)", "Noturno (Festa)"),
    ("rosto pequeno e dividido em meio a uma multidão", "Conflito (Caos)", "Conexão (Close-up)"),
    ("pessoa sozinha ao entardecer, sombras longas", "NAO_DISTANCIAMENTO(horario_errado)", "Distanciamento (Low-key)"),
]

# ---------------------------------------------------------------------------
# GRUPO C - Casos tecnicos / jargao (devem ir para __tecnico__)
# ---------------------------------------------------------------------------
GROUP_C = [
    "f/1.8, ISO 800, 1/500s",
    "deixa o fundo borrado e o rosto nítido",
    "profundidade de campo rasa",
    "subexposição intencional em low-key",
    "estoure o brilho dos realces",
]


def classify_route(result) -> str:
    if result.technical:
        return "tecnico"
    if result.low_confidence:
        return "fallback_low_confidence"
    return "fast_track"


def run():
    print(f"THRESHOLD_TECNICO={THRESHOLD_TECNICO}  CONFIDENCE_THRESHOLD_LOW={CONFIDENCE_THRESHOLD_LOW}")
    print("Carregando modelo SBERT e ancoras (pode demorar alguns segundos)...")
    service = CategorizationService(anchors_path=ANCHORS_PATH, enable_mistral_fallback=False)

    rows = []

    # --- Grupo A ---
    for expected_anchor, texts in GROUP_A.items():
        for text in texts:
            r = service.categorize(text, top_k=3, route_technical_to_mistral=False)
            top1 = r.top_matches[0]
            top2 = r.top_matches[1] if len(r.top_matches) > 1 else None
            gap = (top1.score - top2.score) if top2 else None
            rows.append({
                "group": "A",
                "text": text,
                "expected_anchor": expected_anchor,
                "expected_trap": None,
                "top1_anchor": top1.anchor_id,
                "top1_score": top1.score,
                "top2_anchor": top2.anchor_id if top2 else None,
                "top2_score": top2.score if top2 else None,
                "gap": gap,
                "technical": r.technical,
                "technical_score": r.technical_score,
                "low_confidence": r.low_confidence,
                "route": classify_route(r),
                "hit_expected": top1.anchor_id == expected_anchor,
                "hit_trap": False,
            })

    # --- Grupo B ---
    for text, expected_anchor, trap_anchor in GROUP_B:
        r = service.categorize(text, top_k=3, route_technical_to_mistral=False)
        top1 = r.top_matches[0]
        top2 = r.top_matches[1] if len(r.top_matches) > 1 else None
        gap = (top1.score - top2.score) if top2 else None
        rows.append({
            "group": "B",
            "text": text,
            "expected_anchor": expected_anchor,
            "expected_trap": trap_anchor,
            "top1_anchor": top1.anchor_id,
            "top1_score": top1.score,
            "top2_anchor": top2.anchor_id if top2 else None,
            "top2_score": top2.score if top2 else None,
            "gap": gap,
            "technical": r.technical,
            "technical_score": r.technical_score,
            "low_confidence": r.low_confidence,
            "route": classify_route(r),
            "hit_expected": top1.anchor_id == expected_anchor,
            "hit_trap": top1.anchor_id == trap_anchor,
        })

    # --- Grupo C ---
    for text in GROUP_C:
        r = service.categorize(text, top_k=3, route_technical_to_mistral=False)
        top1 = r.top_matches[0]
        top2 = r.top_matches[1] if len(r.top_matches) > 1 else None
        gap = (top1.score - top2.score) if top2 else None
        rows.append({
            "group": "C",
            "text": text,
            "expected_anchor": "__tecnico__",
            "expected_trap": None,
            "top1_anchor": top1.anchor_id,
            "top1_score": top1.score,
            "top2_anchor": top2.anchor_id if top2 else None,
            "top2_score": top2.score if top2 else None,
            "gap": gap,
            "technical": r.technical,
            "technical_score": r.technical_score,
            "low_confidence": r.low_confidence,
            "route": classify_route(r),
            "hit_expected": r.technical is True,
            "hit_trap": False,
        })

    out_path = os.path.join(ROOT, "data", "processed", "router_health_diag_results.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False, indent=2)
    print(f"\n{len(rows)} casos rodados. Resultados brutos salvos em: {out_path}")


if __name__ == "__main__":
    run()
