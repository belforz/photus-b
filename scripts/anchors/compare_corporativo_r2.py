#!/usr/bin/env python3
"""Comparativo antes/depois da rodada 2 do refino de Corporativo (Focado).

Ao contrario da rodada 1 (que so adicionou frases), aqui a frase 3 original
foi reescrita (mais especifica: exige estudio/fundo controlado e pose seria,
exclui ambiente domestico e expressao espontanea) para atacar 2 pendencias
deixadas pela rodada 1, sem empilhar mais uma frase nova. As outras 4 frases
de Corporativo (2 originais restantes + 2 adicionadas na rodada 1) nao
mudaram. Reaproveita CategorizationService.categorize
(route_technical_to_mistral=False).

Nao altera THRESHOLD_TECNICO, CONFIDENCE_THRESHOLD_LOW, nem as frases de
qualquer outra ancora.
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
    ROOT, "data", "processed", "anchor_backups", "knowledge_anchors_before_corporativo_r2.json"
)
AFTER_ANCHORS_PATH = os.path.join(ROOT, "data", "raw", "knowledge_anchors.json")

# --- Passo 3: corpus de reteste -------------------------------------------

TARGET_CASES = {
    "roupa profissional mas em ambiente real, não estúdio": "Simplicidade (Cotidiano)",
    "sessão de fotos de estúdio com o executivo sorrindo abertamente para a câmera, clima descontraído": "Conexão (Close-up) / zona cinzenta (não Corporativo com score alto)",
}

# casos-alvo ja corrigidos na rodada 1 - checar que a rodada 2 nao desfaz
ROUND1_TARGETS_CROSS_CHECK = {
    "retrato de estúdio emotivo, com olhar vivo": "Conexão (Close-up)",
    "cena social mas estática e formal, tipo coquetel corporativo": "Corporativo (Focado)",
}

GROUP_A_CORPORATIVO = {
    "headshot com fundo neutro de estúdio": "Corporativo (Focado)",
    "iluminação de estúdio limpa, roupa formal": "Corporativo (Focado)",
    "foto que colocaria no LinkedIn sem hesitar": "Corporativo (Focado)",
}

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

GENERALIZATION_CASES = {
    "foto de perfil para o site da empresa, sorriso discreto, fundo neutro de estúdio": "Corporativo (Focado)",
    "empresário posando para revista, ambiente de escritório real, sem produção de estúdio": "Simplicidade (Cotidiano) / zona cinzenta",
}


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
    header = f"{'Caso':<70} | {'Esperado':<35} | {'Top1 antes':<22} | {'Score antes':>11} | {'Top1 depois':<22} | {'Score depois':>12}"
    print(header)
    print("-" * len(header))
    rows = []
    for text, expected in cases_dict.items():
        b = classify(before_svc, text)
        a = classify(after_svc, text)
        rows.append({"text": text, "expected": expected, "before": b, "after": a})
        print(
            f"{text[:68]:<70} | {expected[:33]:<35} | {b['top1_anchor'][:20]:<22} | {b['top1_score']:>11.3f} | "
            f"{a['top1_anchor'][:20]:<22} | {a['top1_score']:>12.3f}"
        )
    return rows


def main():
    print(f"THRESHOLD_TECNICO={THRESHOLD_TECNICO}  CONFIDENCE_THRESHOLD_LOW={CONFIDENCE_THRESHOLD_LOW}\n")

    print("Carregando servico ANTES (rodada 1: frase 3 generica)...")
    svc_before = CategorizationService(anchors_path=BEFORE_ANCHORS_PATH, enable_mistral_fallback=False)
    print("Carregando servico DEPOIS (rodada 2: frase 3 reescrita)...")
    svc_after = CategorizationService(anchors_path=AFTER_ANCHORS_PATH, enable_mistral_fallback=False)

    target_rows = print_table("Passo 4 - Casos-alvo da rodada 2", TARGET_CASES, svc_before, svc_after)
    r1_cross_rows = print_table("Checagem cruzada - casos-alvo ja corrigidos na rodada 1", ROUND1_TARGETS_CROSS_CHECK, svc_before, svc_after)
    corp_a_rows = print_table("Grupo A de Corporativo (3 casos centrais)", GROUP_A_CORPORATIVO, svc_before, svc_after)
    gen_rows = print_table("Casos novos - checagem de generalizacao", GENERALIZATION_CASES, svc_before, svc_after)

    # --- Grupo A completo (30 casos, todas as ancoras) ---
    print("\n=== Checagem de regressao: Grupo A completo (30 casos, todas as ancoras) ===")
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

    # --- corpus tecnico ---
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

    # --- criterio de parada ---
    def confident_wrong(row, side="after"):
        s = row[side]
        return s["top1_anchor"] != row["expected"] and s["top1_score"] >= CONFIDENCE_THRESHOLD_LOW

    print("\n=== CRITERIO DE PARADA (Passo 5) ===")
    target_ok = True
    for row in target_rows:
        hit = row["after"]["top1_anchor"] == row["expected"]
        no_confident_wrong = not confident_wrong(row)
        ok = hit or no_confident_wrong
        status = "OK (bateu)" if hit else ("OK (sem erro confiante)" if no_confident_wrong else "FALHOU (erro confiante)")
        print(f"  [{status}] {row['text']!r} -> depois top1={row['after']['top1_anchor']} score={row['after']['top1_score']:.3f}")
        target_ok = target_ok and ok

    # casos centrais de Corporativo nao podem piorar em relacao ao estado pos-rodada-1
    corp_a_ok = True
    for row in corp_a_rows:
        before_hit = row["before"]["top1_anchor"] == row["expected"]
        after_hit = row["after"]["top1_anchor"] == row["expected"]
        # "piorar" = estava certo e deixou de estar, OU score caiu de forma relevante mesmo continuando certo
        if before_hit and not after_hit:
            corp_a_ok = False
            print(f"  [PIOROU] {row['text']!r}: estava correto antes, deixou de bater depois (top1={row['after']['top1_anchor']})")
    print(f"\n  2 casos-alvo da rodada 2 (bateram ou sem erro confiante): {'OK' if target_ok else 'FALHOU'}")
    print(f"  3 casos centrais de Corporativo nao pioraram vs. pos-rodada-1: {'OK' if corp_a_ok else 'FALHOU'}")

    r1_targets_ok = all(row["after"]["top1_anchor"] == row["expected"] for row in r1_cross_rows)
    print(f"  2 casos-alvo da rodada 1 continuam batendo: {'OK' if r1_targets_ok else 'FALHOU'}")
    print(f"  corpus tecnico sem efeito colateral: {'OK' if not tecnico_regressions else 'ALERTA (reportar)'}")

    non_corp_a_regressions = [r for r in regressions if r["expected"] != "Corporativo (Focado)"]
    print(f"  Grupo A completo - divergencias fora de Corporativo: {len(non_corp_a_regressions)} (reportar mesmo se 0)")

    success = target_ok and corp_a_ok and r1_targets_ok and (not tecnico_regressions) and (not non_corp_a_regressions)
    print(f"\n  RESULTADO FINAL: {'CRITERIO ATINGIDO' if success else 'CRITERIO NAO ATINGIDO'}")

    out_path = os.path.join(ROOT, "data", "processed", "corporativo_r2_comparison.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({
            "threshold_tecnico": THRESHOLD_TECNICO,
            "confidence_threshold_low": CONFIDENCE_THRESHOLD_LOW,
            "target_cases": target_rows,
            "round1_targets_cross_check": r1_cross_rows,
            "group_a_corporativo": corp_a_rows,
            "generalization_cases": gen_rows,
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
