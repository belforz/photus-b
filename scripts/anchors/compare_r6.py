#!/usr/bin/env python3
"""Comparativo antes/depois da rodada 6: reescrever 2 frases-lista de Simplicidade.

Mesma causa raiz corrigida na rodada 1 de __tecnico__: 2 das 4 frases de
Simplicidade eram listas de palavras soltas ("casa, cozinha, rua, trabalho,
rotina" / "natural, simples, casual, autêntico, doméstico, familiar, sem
pose"), diluidas por mean pooling. Reescritas em prosa natural, mantendo as
outras 2 frases (ja em prosa) intactas.

Reaproveita CategorizationService.categorize (route_technical_to_mistral=False).
Nao altera THRESHOLD_TECNICO, CONFIDENCE_THRESHOLD_LOW, nem qualquer outra
ancora alem de Simplicidade.
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
    ROOT, "data", "processed", "anchor_backups", "knowledge_anchors_before_r6.json"
)
AFTER_ANCHORS_PATH = os.path.join(ROOT, "data", "raw", "knowledge_anchors.json")

GROUP_A_SIMPLICIDADE = {
    "cozinha iluminada por luz de janela, sem produção": "Simplicidade (Cotidiano)",
    "pessoa lendo sem posar": "Simplicidade (Cotidiano)",
    "cena doméstica comum sem drama": "Simplicidade (Cotidiano)",
}

FRONTEIRA_CASES = {
    "pessoa em roupa profissional mas em ambiente real, não estúdio": "Simplicidade (Cotidiano)",
    "roupa profissional mas em ambiente real, não estúdio": "Simplicidade (Cotidiano)",
}

PRIOR_ROUNDS_TARGETS = {
    "retrato de estúdio emotivo, com olhar vivo": "Conexão (Close-up)",
    "cena social mas estática e formal, tipo coquetel corporativo": "Corporativo (Focado)",
    "sessão de fotos de estúdio com o executivo sorrindo abertamente para a câmera, clima descontraído": "Conexão (Close-up)",
    "cena doméstica mas visivelmente produzida e estilizada": "Solenidade (Estase)",
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


def classify(service, text):
    r = service.categorize(text, top_k=3, route_technical_to_mistral=False)
    top1 = r.top_matches[0]
    return {
        "top1_anchor": top1.anchor_id,
        "top1_score": top1.score,
        "technical": r.technical,
        "technical_score": r.technical_score,
        "low_confidence": r.low_confidence,
    }


def print_table(title, cases_dict, before_svc, after_svc):
    print(f"\n=== {title} ===")
    header = f"{'Caso':<65} | {'Esperado':<24} | {'Top1 antes':<22} | {'Score antes':>11} | {'Top1 depois':<22} | {'Score depois':>12}"
    print(header)
    print("-" * len(header))
    rows = []
    for text, expected in cases_dict.items():
        b = classify(before_svc, text)
        a = classify(after_svc, text)
        rows.append({"text": text, "expected": expected, "before": b, "after": a})
        print(
            f"{text[:63]:<65} | {expected[:22]:<24} | {b['top1_anchor'][:20]:<22} | {b['top1_score']:>11.3f} | "
            f"{a['top1_anchor'][:20]:<22} | {a['top1_score']:>12.3f}"
        )
    return rows


def main():
    print(f"THRESHOLD_TECNICO={THRESHOLD_TECNICO}  CONFIDENCE_THRESHOLD_LOW={CONFIDENCE_THRESHOLD_LOW}\n")

    print("Carregando servico ANTES (Simplicidade: 2 frases-lista)...")
    svc_before = CategorizationService(anchors_path=BEFORE_ANCHORS_PATH, enable_mistral_fallback=False)
    print("Carregando servico DEPOIS (Simplicidade: 2 frases reescritas em prosa)...")
    svc_after = CategorizationService(anchors_path=AFTER_ANCHORS_PATH, enable_mistral_fallback=False)

    simp_rows = print_table("Passo Teste - Grupo A de Simplicidade (3 casos centrais)", GROUP_A_SIMPLICIDADE, svc_before, svc_after)
    fronteira_rows = print_table("Caso de fronteira (oficial + customizado) - limitacao conhecida", FRONTEIRA_CASES, svc_before, svc_after)
    prior_rows = print_table("Checagem cruzada - casos-alvo corrigidos nas rodadas 1-5", PRIOR_ROUNDS_TARGETS, svc_before, svc_after)
    corp_a_rows = print_table("Grupo A de Corporativo (3 casos centrais)", GROUP_A_CORPORATIVO, svc_before, svc_after)

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

    print("\n=== Checagem cruzada: corpus tecnico ===")
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
    print(f"  {tecnico_identical}/{len(TECNICO_CROSS_CHECK)} casos tecnicos identicos.")
    if not tecnico_regressions:
        print("  Nenhuma divergencia no corpus tecnico.")
    else:
        for r in tecnico_regressions:
            print(f"    {r['text']!r}: antes={r['before']} -> depois={r['after']}")

    # score medio Simplicidade Grupo A
    score_before = sum(row["before"]["top1_score"] for row in simp_rows) / len(simp_rows)
    score_after = sum(row["after"]["top1_score"] for row in simp_rows) / len(simp_rows)
    hits_before = sum(1 for row in simp_rows if row["before"]["top1_anchor"] == row["expected"])
    hits_after = sum(1 for row in simp_rows if row["after"]["top1_anchor"] == row["expected"])
    lowconf_before = sum(1 for row in simp_rows if row["before"]["low_confidence"])
    lowconf_after = sum(1 for row in simp_rows if row["after"]["low_confidence"])

    print("\n=== CRITERIO DE PARADA ===")
    print(f"  Score medio Simplicidade (Grupo A): antes={score_before:.3f} depois={score_after:.3f} ({'subiu' if score_after > score_before else 'nao subiu'})")
    print(f"  Acerto Grupo A Simplicidade: antes={hits_before}/3 depois={hits_after}/3")
    print(f"  low_confidence Simplicidade: antes={lowconf_before}/3 depois={lowconf_after}/3")

    prior_ok = all(row["after"]["top1_anchor"] == row["expected"] for row in prior_rows)
    corp_a_ok = all(row["after"]["top1_anchor"] == row["expected"] for row in corp_a_rows)
    no_group_a_regression = len(regressions) == 0
    no_tecnico_regression = len(tecnico_regressions) == 0
    score_improved = score_after > score_before

    print(f"\n  score medio subiu: {'OK' if score_improved else 'FALHOU'}")
    print(f"  checagem cruzada rodadas 1-5 (casos-alvo): {'OK' if prior_ok else 'FALHOU'}")
    print(f"  3 casos centrais de Corporativo continuam corretos: {'OK' if corp_a_ok else 'FALHOU'}")
    print(f"  Grupo A completo (30 casos) sem divergencia: {'OK' if no_group_a_regression else 'FALHOU'}")
    print(f"  corpus tecnico sem efeito colateral: {'OK' if no_tecnico_regression else 'ALERTA'}")

    success = score_improved and prior_ok and corp_a_ok and no_group_a_regression and no_tecnico_regression
    print(f"\n  RESULTADO FINAL: {'CRITERIO ATINGIDO' if success else 'CRITERIO NAO ATINGIDO'}")

    out_path = os.path.join(ROOT, "data", "processed", "r6_comparison.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({
            "threshold_tecnico": THRESHOLD_TECNICO,
            "confidence_threshold_low": CONFIDENCE_THRESHOLD_LOW,
            "simplicidade_group_a": simp_rows,
            "fronteira_cases": fronteira_rows,
            "prior_rounds_targets": prior_rows,
            "group_a_corporativo": corp_a_rows,
            "group_a_full_regressions": regressions,
            "group_a_full_identical_count": identical,
            "group_a_full_total": total_a,
            "tecnico_cross_check_regressions": tecnico_regressions,
            "tecnico_cross_check_identical_count": tecnico_identical,
            "score_before": score_before,
            "score_after": score_after,
            "criterio_atingido": success,
        }, f, ensure_ascii=False, indent=2)
    print(f"\nResultados salvos em: {out_path}")


if __name__ == "__main__":
    main()
