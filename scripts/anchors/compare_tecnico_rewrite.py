#!/usr/bin/env python3
"""Comparativo antes/depois da reescrita da ancora __tecnico__.

Roda o mesmo corpus contra o anchors_path "antes" (frases-lista de
palavras-chave, backup do Passo 1) e "depois" (prosa natural, Passo 2),
reaproveitando CategorizationService.categorize (route_technical_to_mistral=False).

Nao altera THRESHOLD_TECNICO nem CONFIDENCE_THRESHOLD_LOW.
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

BEFORE_ANCHORS_PATH = os.path.join(
    ROOT, "data", "processed", "anchor_backups", "knowledge_anchors_before.json"
)
AFTER_ANCHORS_PATH = os.path.join(ROOT, "data", "raw", "knowledge_anchors.json")

# Grupo C original (diagnostico anterior)
GROUP_C_ORIGINAL = [
    "f/1.8, ISO 800, 1/500s",
    "deixa o fundo borrado e o rosto nítido",
    "profundidade de campo rasa",
    "subexposição intencional em low-key",
    "estoure o brilho dos realces",
]

# Casos novos em prosa, nao vistos no diagnostico original
GROUP_C_NOVOS = [
    "quero saber o ajuste de exposição pra não estourar as luzes",
    "como configuro o ISO pra reduzir ruído na foto",
    "deixa o assunto nítido e o fundo totalmente desfocado",
    "ajustar a temperatura de cor pra ficar mais quente",
]

TECNICO_CASES = GROUP_C_ORIGINAL + GROUP_C_NOVOS

# Grupo A (checagem de regressao - deve continuar identico antes/depois)
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


def run_corpus(service, texts):
    out = {}
    for text in texts:
        r = service.categorize(text, top_k=3, route_technical_to_mistral=False)
        out[text] = {
            "technical_score": r.technical_score,
            "technical": r.technical,
            "top1_anchor": r.top_matches[0].anchor_id,
            "top1_score": r.top_matches[0].score,
        }
    return out


def run_group_a(service):
    out = {}
    for expected_anchor, texts in GROUP_A.items():
        for text in texts:
            r = service.categorize(text, top_k=3, route_technical_to_mistral=False)
            top1 = r.top_matches[0]
            out[text] = {
                "expected_anchor": expected_anchor,
                "top1_anchor": top1.anchor_id,
                "top1_score": top1.score,
                "hit_expected": top1.anchor_id == expected_anchor,
            }
    return out


def main():
    print(f"THRESHOLD_TECNICO={THRESHOLD_TECNICO}  CONFIDENCE_THRESHOLD_LOW={CONFIDENCE_THRESHOLD_LOW}\n")

    print("Carregando servico ANTES (frases-lista de palavras-chave)...")
    svc_before = CategorizationService(anchors_path=BEFORE_ANCHORS_PATH, enable_mistral_fallback=False)
    print("Carregando servico DEPOIS (prosa natural)...")
    svc_after = CategorizationService(anchors_path=AFTER_ANCHORS_PATH, enable_mistral_fallback=False)

    # --- Grupo C: tecnico, antes vs depois ---
    before_tecnico = run_corpus(svc_before, TECNICO_CASES)
    after_tecnico = run_corpus(svc_after, TECNICO_CASES)

    rows = []
    for text in TECNICO_CASES:
        b = before_tecnico[text]
        a = after_tecnico[text]
        rows.append({
            "text": text,
            "is_new_case": text in GROUP_C_NOVOS,
            "score_before": b["technical_score"],
            "technical_before": b["technical"],
            "top1_before": b["top1_anchor"],
            "top1_score_before": b["top1_score"],
            "score_after": a["technical_score"],
            "technical_after": a["technical"],
            "top1_after": a["top1_anchor"],
            "top1_score_after": a["top1_score"],
        })

    print("\n=== TABELA COMPARATIVA (Passo 4) — casos tecnicos ===")
    header = f"{'Caso':<58} | {'Score antes':>11} | {'Tech? antes':>11} | {'Score depois':>12} | {'Tech? depois':>12} | {'Top1 depois':<25}"
    print(header)
    print("-" * len(header))
    for row in rows:
        tag = " [NOVO]" if row["is_new_case"] else ""
        print(
            f"{row['text'][:56] + tag:<58} | {row['score_before']:>11.3f} | {str(row['technical_before']):>11} | "
            f"{row['score_after']:>12.3f} | {str(row['technical_after']):>12} | {row['top1_after']:<25}"
        )

    # anti-padrao do diagnostico anterior: technical=False E top1 confiante numa ancora errada.
    # Se technical=True, o roteador ja manda pro fluxo tecnico independente do top1/category
    # (ver classify_route() em diagnose_router_health.py e docs/API.md).
    print("\n=== Checagem de erro confiante (technical=False E top1 != __tecnico__ com score alto), DEPOIS ===")
    confident_misroutes = []
    for row in rows:
        if (not row["technical_after"] and row["top1_after"] != "__tecnico__"
                and row["top1_score_after"] >= CONFIDENCE_THRESHOLD_LOW):
            confident_misroutes.append(row)
            print(f"  [ALERTA] {row['text']!r} -> technical=False, top1={row['top1_after']} score={row['top1_score_after']:.3f}")
    if not confident_misroutes:
        print("  Nenhum caso tecnico roteado (technical=False) com alta confianca para uma ancora errada.")

    # --- Grupo A: regressao ---
    before_a = run_group_a(svc_before)
    after_a = run_group_a(svc_after)

    print("\n=== Checagem de regressao (Passo 5) — Grupo A antes vs depois ===")
    regressions = []
    identical = 0
    for text, b in before_a.items():
        a = after_a[text]
        same_top1 = b["top1_anchor"] == a["top1_anchor"]
        same_score = abs(b["top1_score"] - a["top1_score"]) < 1e-6
        if same_top1 and same_score:
            identical += 1
        else:
            regressions.append((text, b, a))
    print(f"  {identical}/{len(before_a)} casos do Grupo A identicos (mesmo top1_anchor e mesmo score).")
    if regressions:
        print("  Divergencias encontradas:")
        for text, b, a in regressions:
            print(f"    {text!r}: antes top1={b['top1_anchor']} ({b['top1_score']:.4f}) -> "
                  f"depois top1={a['top1_anchor']} ({a['top1_score']:.4f})")
    else:
        print("  Nenhuma divergencia. As outras 10 ancoras nao tiveram efeito colateral.")

    # --- Criterio de parada ---
    total = len(rows)
    hits_after = sum(1 for r in rows if r["technical_after"])
    hits_before = sum(1 for r in rows if r["technical_before"])
    majority_ok = hits_after > total / 2
    no_confident_misroute = len(confident_misroutes) == 0
    no_regression = len(regressions) == 0

    print("\n=== CRITERIO DE PARADA (Passo 5) ===")
    print(f"  technical=True depois: {hits_after}/{total} (antes: {hits_before}/{total})")
    print(f"  maioria roteando corretamente (depois): {'OK' if majority_ok else 'FALHOU'}")
    print(f"  sem erro confiante em ancora errada: {'OK' if no_confident_misroute else 'FALHOU'}")
    print(f"  sem regressao no Grupo A: {'OK' if no_regression else 'FALHOU'}")
    success = majority_ok and no_confident_misroute and no_regression
    print(f"  RESULTADO FINAL: {'CRITERIO ATINGIDO' if success else 'CRITERIO NAO ATINGIDO'}")

    out_path = os.path.join(ROOT, "data", "processed", "tecnico_rewrite_comparison.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({
            "threshold_tecnico": THRESHOLD_TECNICO,
            "confidence_threshold_low": CONFIDENCE_THRESHOLD_LOW,
            "tecnico_rows": rows,
            "confident_misroutes": [r["text"] for r in confident_misroutes],
            "group_a_regressions": [t for t, _, _ in regressions],
            "group_a_identical_count": identical,
            "group_a_total": len(before_a),
            "criterio_atingido": success,
        }, f, ensure_ascii=False, indent=2)
    print(f"\nResultados salvos em: {out_path}")


if __name__ == "__main__":
    main()
