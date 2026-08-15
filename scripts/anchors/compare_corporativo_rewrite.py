#!/usr/bin/env python3
"""Comparativo antes/depois do refino da ancora Corporativo (Focado).

Ao contrario da rodada de __tecnico__, aqui NAO reescrevemos as 3 frases
existentes: apenas adicionamos 2 frases novas (uma contra o vazamento pra
Conexao, outra contra o vazamento pra Noturno). Reaproveita
CategorizationService.categorize (route_technical_to_mistral=False), no
mesmo formato do compare_tecnico_rewrite.py.

Nao altera THRESHOLD_TECNICO, CONFIDENCE_THRESHOLD_LOW, nem as frases das
outras ancoras.
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
    ROOT, "data", "processed", "anchor_backups", "knowledge_anchors_before_corporativo.json"
)
AFTER_ANCHORS_PATH = os.path.join(ROOT, "data", "raw", "knowledge_anchors.json")

# --- Passo 3: corpus de reteste -------------------------------------------

# casos-alvo desta rodada (criterio de aprovacao)
TARGET_CASES = {
    "retrato de estúdio emotivo, com olhar vivo": "Conexão (Close-up)",
    "cena social mas estática e formal, tipo coquetel corporativo": "Corporativo (Focado)",
}

# fora de escopo nesta rodada - so observacao, nao e criterio de aprovacao
OBSERVATION_CASE = {
    "roupa profissional mas em ambiente real, não estúdio": "Simplicidade (Cotidiano)",
}

# casos novos pra checar generalizacao (nao decorar as 2 frases-alvo)
GENERALIZATION_CASES = {
    "sessão de fotos de estúdio com o executivo sorrindo abertamente para a câmera, clima descontraído": "Conexão (Close-up) / zona cinzenta (não Corporativo puro)",
    "confraternização de fim de ano da empresa, ambiente sério, brinde protocolar": "Corporativo (Focado)",
    "festa da empresa com a equipe dançando e comemorando": "Noturno (Festa)",
}

# Grupo A original de Corporativo (3 casos centrais do diagnostico)
GROUP_A_CORPORATIVO = {
    "headshot com fundo neutro de estúdio": "Corporativo (Focado)",
    "iluminação de estúdio limpa, roupa formal": "Corporativo (Focado)",
    "foto que colocaria no LinkedIn sem hesitar": "Corporativo (Focado)",
}

# Grupo A completo do diagnostico original (30 casos, todas as ancoras)
GROUP_A_FULL = {
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

# corpus tecnico da rodada anterior - checagem cruzada (Passo 6)
TECNICO_CROSS_CHECK = [
    "f/1.8, ISO 800, 1/500s",
    "deixa o fundo borrado e o rosto nítido",
    "profundidade de campo rasa",
    "subexposição intencional em low-key",
    "estoure o brilho dos realces",
    "quero saber o ajuste de exposição pra não estourar as luzes",
    "como configuro o ISO pra reduzir ruído na foto",
    "deixa o assunto nítido e o fundo totalmente desfocado",
    "ajustar a temperatura de cor pra ficar mais quente",
]


def classify(service, text):
    r = service.categorize(text, top_k=3, route_technical_to_mistral=False)
    top1 = r.top_matches[0]
    return {
        "top1_anchor": top1.anchor_id,
        "top1_score": top1.score,
        "technical": r.technical,
        "technical_score": r.technical_score,
    }


def print_table(title, cases_dict, before_svc, after_svc):
    print(f"\n=== {title} ===")
    header = f"{'Caso':<70} | {'Esperado':<28} | {'Top1 antes':<22} | {'Score antes':>11} | {'Top1 depois':<22} | {'Score depois':>12}"
    print(header)
    print("-" * len(header))
    rows = []
    for text, expected in cases_dict.items():
        b = classify(before_svc, text)
        a = classify(after_svc, text)
        rows.append({"text": text, "expected": expected, "before": b, "after": a})
        print(
            f"{text[:68]:<70} | {expected[:26]:<28} | {b['top1_anchor'][:20]:<22} | {b['top1_score']:>11.3f} | "
            f"{a['top1_anchor'][:20]:<22} | {a['top1_score']:>12.3f}"
        )
    return rows


def main():
    print(f"THRESHOLD_TECNICO={THRESHOLD_TECNICO}  CONFIDENCE_THRESHOLD_LOW={CONFIDENCE_THRESHOLD_LOW}\n")

    print("Carregando servico ANTES (3 frases de Corporativo)...")
    svc_before = CategorizationService(anchors_path=BEFORE_ANCHORS_PATH, enable_mistral_fallback=False)
    print("Carregando servico DEPOIS (5 frases de Corporativo)...")
    svc_after = CategorizationService(anchors_path=AFTER_ANCHORS_PATH, enable_mistral_fallback=False)

    target_rows = print_table("Passo 4 - Casos-alvo (criterio de aprovacao)", TARGET_CASES, svc_before, svc_after)
    obs_rows = print_table("Passo 4 - Caso de observacao (Simplicidade, fora de escopo)", OBSERVATION_CASE, svc_before, svc_after)
    gen_rows = print_table("Passo 4 - Casos novos (checagem de generalizacao)", GENERALIZATION_CASES, svc_before, svc_after)
    corp_a_rows = print_table("Passo 3 - Grupo A original de Corporativo (3 casos centrais)", GROUP_A_CORPORATIVO, svc_before, svc_after)

    # --- Passo 5: regressao no Grupo A completo (30 casos, todas as ancoras) ---
    print("\n=== Passo 5 - Checagem de regressao: Grupo A completo (30 casos, todas as ancoras) ===")
    regressions = []
    identical = 0
    total_a = 0
    for expected_anchor, texts in GROUP_A_FULL.items():
        for text in texts:
            total_a += 1
            b = classify(svc_before, text)
            a = classify(svc_after, text)
            same_top1 = b["top1_anchor"] == a["top1_anchor"]
            same_score = abs(b["top1_score"] - a["top1_score"]) < 1e-6
            if same_top1 and same_score:
                identical += 1
            else:
                regressions.append({"text": text, "expected": expected_anchor, "before": b, "after": a})
    print(f"  {identical}/{total_a} casos identicos (mesmo top1_anchor e mesmo score).")
    if regressions:
        print("  Divergencias encontradas:")
        for r in regressions:
            print(
                f"    {r['text']!r} (esperado {r['expected']}): antes top1={r['before']['top1_anchor']} "
                f"({r['before']['top1_score']:.4f}) -> depois top1={r['after']['top1_anchor']} ({r['after']['top1_score']:.4f})"
            )
    else:
        print("  Nenhuma divergencia.")

    # --- Passo 6: checagem cruzada com __tecnico__ (ja refinado na rodada anterior) ---
    print("\n=== Checagem cruzada: corpus tecnico (rodada anterior) ===")
    tecnico_regressions = []
    tecnico_identical = 0
    for text in TECNICO_CROSS_CHECK:
        b = classify(svc_before, text)
        a = classify(svc_after, text)
        same_top1 = b["top1_anchor"] == a["top1_anchor"]
        same_technical = b["technical"] == a["technical"]
        same_tech_score = abs(b["technical_score"] - a["technical_score"]) < 1e-6
        if same_top1 and same_technical and same_tech_score:
            tecnico_identical += 1
        else:
            tecnico_regressions.append({"text": text, "before": b, "after": a})
    print(f"  {tecnico_identical}/{len(TECNICO_CROSS_CHECK)} casos tecnicos identicos (top1, technical, technical_score).")
    if tecnico_regressions:
        print("  Divergencias encontradas:")
        for r in tecnico_regressions:
            print(
                f"    {r['text']!r}: antes top1={r['before']['top1_anchor']} technical={r['before']['technical']} "
                f"({r['before']['technical_score']:.4f}) -> depois top1={r['after']['top1_anchor']} technical={r['after']['technical']} "
                f"({r['after']['technical_score']:.4f})"
            )
    else:
        print("  Nenhuma divergencia no corpus tecnico.")

    # --- Passo 6: criterio de parada ---
    def confident_wrong(row):
        """True se, DEPOIS, o caso nao bateu na ancora esperada E o erro e confiante (score >= CONFIDENCE_THRESHOLD_LOW)."""
        a = row["after"]
        return a["top1_anchor"] != row["expected"] and a["top1_score"] >= CONFIDENCE_THRESHOLD_LOW

    print("\n=== CRITERIO DE PARADA (Passo 6) ===")
    target_ok = True
    for row in target_rows:
        hit = row["after"]["top1_anchor"] == row["expected"]
        no_confident_wrong = not confident_wrong(row)
        ok = hit or no_confident_wrong
        status = "OK (bateu)" if hit else ("OK (nao bateu, mas sem erro confiante)" if no_confident_wrong else "FALHOU (erro confiante)")
        print(f"  [{status}] {row['text']!r} -> depois top1={row['after']['top1_anchor']} score={row['after']['top1_score']:.3f}")
        target_ok = target_ok and ok

    no_group_a_regression = len(regressions) == 0
    no_tecnico_regression = len(tecnico_regressions) == 0

    obs_row = obs_rows[0]
    obs_before_hit = obs_row["before"]["top1_anchor"] == obs_row["expected"]
    obs_after_hit = obs_row["after"]["top1_anchor"] == obs_row["expected"]
    obs_before_confident_wrong = (not obs_before_hit) and obs_row["before"]["top1_score"] >= CONFIDENCE_THRESHOLD_LOW
    obs_after_confident_wrong = (not obs_after_hit) and obs_row["after"]["top1_score"] >= CONFIDENCE_THRESHOLD_LOW
    obs_not_worse = obs_after_hit or (not obs_after_confident_wrong) or obs_before_confident_wrong
    # "nao piorou": nao pode ter virado erro confiante se antes nao era
    obs_regressed = obs_after_confident_wrong and not obs_before_confident_wrong

    print(f"\n  2 casos-alvo do Passo 3 (bateram ou pelo menos sem erro confiante): {'OK' if target_ok else 'FALHOU'}")
    print(f"  zero mudanca de comportamento no Grupo A completo (30 casos, todas as ancoras): {'OK' if no_group_a_regression else 'FALHOU'}")
    print(f"  caso de observacao (Simplicidade) nao piorou: {'OK' if not obs_regressed else 'FALHOU'}")
    print(f"  sem efeito colateral no corpus tecnico (checagem cruzada): {'OK' if no_tecnico_regression else 'ALERTA (reportar)'}")

    success = target_ok and no_group_a_regression and (not obs_regressed)
    print(f"\n  RESULTADO FINAL: {'CRITERIO ATINGIDO' if success else 'CRITERIO NAO ATINGIDO'}")

    out_path = os.path.join(ROOT, "data", "processed", "corporativo_rewrite_comparison.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({
            "threshold_tecnico": THRESHOLD_TECNICO,
            "confidence_threshold_low": CONFIDENCE_THRESHOLD_LOW,
            "target_cases": target_rows,
            "observation_case": obs_rows,
            "generalization_cases": gen_rows,
            "group_a_corporativo": corp_a_rows,
            "group_a_full_regressions": regressions,
            "group_a_full_identical_count": identical,
            "group_a_full_total": total_a,
            "tecnico_cross_check_regressions": tecnico_regressions,
            "tecnico_cross_check_identical_count": tecnico_identical,
            "criterio_atingido": success,
        }, f, ensure_ascii=False, indent=2)
    print(f"\nResultados salvos em: {out_path}")


if __name__ == "__main__":
    main()
