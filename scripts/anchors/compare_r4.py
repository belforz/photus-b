#!/usr/bin/env python3
"""Comparativo antes/depois da rodada 4: reforco isolado de Conexao.

Repete a rodada 3, mas SO com a frase nova de Conexao (a que funcionou sem
efeito colateral) - sem a frase de Simplicidade (a que causou a regressao em
Corporativo por sobreposicao lexical de "roupa formal"). Objetivo: fechar o
caso do "executivo sorrindo, clima descontraido" sem carregar a causa da
regressao da rodada 3.

Reaproveita CategorizationService.categorize (route_technical_to_mistral=False).
Nao altera THRESHOLD_TECNICO, CONFIDENCE_THRESHOLD_LOW, Simplicidade,
Corporativo, nem qualquer outra ancora alem de Conexao.
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
    ROOT, "data", "processed", "anchor_backups", "knowledge_anchors_before_r4.json"
)
AFTER_ANCHORS_PATH = os.path.join(ROOT, "data", "raw", "knowledge_anchors.json")

TARGET_CASE = {
    "sessão de fotos de estúdio com o executivo sorrindo abertamente para a câmera, clima descontraído": "Conexão (Close-up)",
}
TARGET_CASE_NOTE = "esperado Conexão ou zona cinzenta (qualquer coisa != Corporativo com score alto conta como sucesso)"

# checagem especifica da regressao da rodada 3 (nao deve reaparecer, ja que Simplicidade nao mudou)
R3_REGRESSION_CHECK = {
    "iluminação de estúdio limpa, roupa formal": "Corporativo (Focado)",
}

GUARD_CASES = {
    "foto de perfil para o site da empresa, sorriso discreto, fundo neutro de estúdio": "Corporativo (Focado)",
    "cena doméstica mas visivelmente produzida e estilizada": "Solenidade (Estase)",
    "rosto pequeno e disperso em meio a uma multidão": "Conflito (Caos)",
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
    header = f"{'Caso':<65} | {'Esperado':<32} | {'Top1 antes':<22} | {'Score antes':>11} | {'Top1 depois':<22} | {'Score depois':>12}"
    print(header)
    print("-" * len(header))
    rows = []
    for text, expected in cases_dict.items():
        b = classify(before_svc, text)
        a = classify(after_svc, text)
        rows.append({"text": text, "expected": expected, "before": b, "after": a})
        print(
            f"{text[:63]:<65} | {expected[:30]:<32} | {b['top1_anchor'][:20]:<22} | {b['top1_score']:>11.3f} | "
            f"{a['top1_anchor'][:20]:<22} | {a['top1_score']:>12.3f}"
        )
    return rows


def main():
    print(f"THRESHOLD_TECNICO={THRESHOLD_TECNICO}  CONFIDENCE_THRESHOLD_LOW={CONFIDENCE_THRESHOLD_LOW}\n")

    print("Carregando servico ANTES (Conexao 3 frases)...")
    svc_before = CategorizationService(anchors_path=BEFORE_ANCHORS_PATH, enable_mistral_fallback=False)
    print("Carregando servico DEPOIS (Conexao 4 frases)...")
    svc_after = CategorizationService(anchors_path=AFTER_ANCHORS_PATH, enable_mistral_fallback=False)

    target_rows = print_table("Passo 4 - Caso-alvo da rodada 4", TARGET_CASE, svc_before, svc_after)
    r3_check_rows = print_table("Checagem especifica: regressao da rodada 3 nao deve reaparecer", R3_REGRESSION_CHECK, svc_before, svc_after)
    guard_rows = print_table("Passo 3 - Casos de guarda", GUARD_CASES, svc_before, svc_after)
    corp_a_rows = print_table("Grupo A de Corporativo (3 casos centrais)", GROUP_A_CORPORATIVO, svc_before, svc_after)

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
    print(f"  {tecnico_identical}/{len(TECNICO_CROSS_CHECK)} casos tecnicos identicos.")
    if tecnico_regressions:
        for r in tecnico_regressions:
            print(f"    {r['text']!r}: antes={r['before']} -> depois={r['after']}")
    else:
        print("  Nenhuma divergencia no corpus tecnico.")

    def confident_wrong(row):
        a = row["after"]
        return a["top1_anchor"] != row["expected"] and a["top1_score"] >= CONFIDENCE_THRESHOLD_LOW

    print("\n=== CRITERIO DE PARADA (Passo 6) ===")
    target_row = target_rows[0]
    target_hit = target_row["after"]["top1_anchor"] == target_row["expected"]
    target_ok = target_hit or not confident_wrong(target_row)
    print(f"  [{'OK' if target_ok else 'FALHOU'}] caso-alvo -> depois top1={target_row['after']['top1_anchor']} score={target_row['after']['top1_score']:.3f}")

    r3_check_row = r3_check_rows[0]
    r3_regression_absent = r3_check_row["after"]["top1_anchor"] == r3_check_row["expected"]
    print(f"  [{'OK' if r3_regression_absent else 'FALHOU'}] regressao da rodada 3 ausente -> depois top1={r3_check_row['after']['top1_anchor']} score={r3_check_row['after']['top1_score']:.3f}")

    guard_ok = True
    for row in guard_rows:
        hit_before = row["before"]["top1_anchor"] == row["expected"]
        hit_after = row["after"]["top1_anchor"] == row["expected"]
        score_delta = row["after"]["top1_score"] - row["before"]["top1_score"]
        # so preocupa se piorou em relacao ao estado pre-existente (nao exige que estivesse certo antes)
        worsened = (hit_before and not hit_after) or (not hit_before and not hit_after and score_delta > 0.02)
        if worsened:
            guard_ok = False
        status = "OK" if not worsened else "PIOROU"
        print(f"  [guarda: {status}] {row['text']!r} -> antes={row['before']['top1_anchor']} {row['before']['top1_score']:.3f} | depois={row['after']['top1_anchor']} {row['after']['top1_score']:.3f} (delta={score_delta:+.3f})")

    corp_a_ok = all(row["after"]["top1_anchor"] == row["expected"] for row in corp_a_rows)
    no_group_a_regression = len(regressions) == 0
    no_tecnico_regression = len(tecnico_regressions) == 0

    print(f"\n  caso-alvo da rodada 4: {'OK' if target_ok else 'FALHOU'}")
    print(f"  regressao da rodada 3 ausente: {'OK' if r3_regression_absent else 'FALHOU'}")
    print(f"  casos de guarda sem piora: {'OK' if guard_ok else 'FALHOU'}")
    print(f"  3 casos centrais de Corporativo continuam corretos: {'OK' if corp_a_ok else 'FALHOU'}")
    print(f"  Grupo A completo (30 casos) sem divergencia: {'OK' if no_group_a_regression else 'FALHOU'}")
    print(f"  corpus tecnico sem efeito colateral: {'OK' if no_tecnico_regression else 'ALERTA'}")

    success = target_ok and r3_regression_absent and guard_ok and corp_a_ok and no_group_a_regression and no_tecnico_regression
    print(f"\n  RESULTADO FINAL: {'CRITERIO ATINGIDO' if success else 'CRITERIO NAO ATINGIDO'}")

    out_path = os.path.join(ROOT, "data", "processed", "r4_comparison.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({
            "threshold_tecnico": THRESHOLD_TECNICO,
            "confidence_threshold_low": CONFIDENCE_THRESHOLD_LOW,
            "target_case": target_rows,
            "r3_regression_check": r3_check_rows,
            "guard_cases": guard_rows,
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
