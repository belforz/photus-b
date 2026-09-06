#!/usr/bin/env python3
"""Comparativo antes/depois da rodada 8: reescrever 2 frases-lista de Nostalgia.

As 2 frases reescritas ("pelicula, polaroid, filme de 35mm" e "saudade, memoria,
passado, afeto antigo, estetica analogica, revelado a mao") viram prosa que
descreve grao de filme / negativo / revelacao quimica como cenario concreto -
o eixo que faltava pros 2 casos centrais que hoje perdem pra Solenidade.

Reaproveita CategorizationService.categorize (route_technical_to_mistral=False).
Nao altera THRESHOLD_TECNICO, CONFIDENCE_THRESHOLD_LOW, nem qualquer outra
ancora alem de Nostalgia.
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
from infrastructure.adapters.sentence_transformer_adapter import SentenceTransformerAdapter  # noqa: E402
from domain.application.use_cases.categorize_text import _cosine  # noqa: E402

BEFORE_ANCHORS_PATH = os.path.join(
    ROOT, "data", "processed", "anchor_backups", "knowledge_anchors_before_r8.json"
)
AFTER_ANCHORS_PATH = os.path.join(ROOT, "data", "raw", "knowledge_anchors.json")

TARGET_CASES = {
    "grão de filme genuíno em retrato quase preto e branco": "Nostalgia (Analógico)",
    "textura de negativo Kodak, tira de contato": "Nostalgia (Analógico)",
}

OBSERVATION_CASE = {
    "estética vintage só que digitalmente perfeita, sem grão real": None,  # AMBIGUO/DESCARTE, so observar
}

GUARD_CASES = {
    "produto isolado em fundo branco": "Solenidade (Estase)",
    "ambiente minimalista vazio e simétrico": "Solenidade (Estase)",
    "silêncio visual, nada em movimento": "Solenidade (Estase)",
    "cena doméstica mas visivelmente produzida e estilizada": "Solenidade (Estase)",
    "atleta no ápice do salto sob sol forte": "Vitalidade (Ação)",
    "corrida com respingos de água": "Vitalidade (Ação)",
    "energia explosiva ao meio-dia": "Vitalidade (Ação)",
}

PRIOR_ROUNDS_TARGETS = {
    "retrato de estúdio emotivo, com olhar vivo": "Conexão (Close-up)",
    "cena social mas estática e formal, tipo coquetel corporativo": "Corporativo (Focado)",
    "sessão de fotos de estúdio com o executivo sorrindo abertamente para a câmera, clima descontraído": "Conexão (Close-up)",
    "cozinha iluminada por luz de janela, sem produção": "Simplicidade (Cotidiano)",
    "poste de luz solitário contra escuridão quase total": "Distanciamento (Low-key)",
    "paisagem grandiosa mas fotografada no escuro": "Distanciamento (Low-key)",
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
    header = f"{'Caso':<65} | {'Esperado':<24} | {'Top1 antes':<22} | {'Score antes':>11} | {'Top1 depois':<22} | {'Score depois':>12}"
    print(header)
    print("-" * len(header))
    rows = []
    for text, expected in cases_dict.items():
        b = classify(before_svc, text)
        a = classify(after_svc, text)
        rows.append({"text": text, "expected": expected, "before": b, "after": a})
        exp_str = expected if expected else "(nenhuma - so observar)"
        print(
            f"{text[:63]:<65} | {exp_str[:22]:<24} | {b['top1_anchor'][:20]:<22} | {b['top1_score']:>11.3f} | "
            f"{a['top1_anchor'][:20]:<22} | {a['top1_score']:>12.3f}"
        )
    return rows


def phrase_breakdown(embedder, anchors, text, anchor_ids):
    emb = embedder.generate_embeddings(texts=text)
    print(f"\n  -- breakdown por frase para {text!r} --")
    scores = []
    for aid, phrase, aemb in zip(anchors["anchors_ids"], anchors["phrases"], anchors["embeddings"]):
        if aid in anchor_ids:
            scores.append((float(_cosine(emb, aemb)), aid, phrase))
    scores.sort(reverse=True)
    for s, aid, p in scores:
        print(f"    {s:.3f}  [{aid}]  {p[:95]}")
    return scores


def main():
    print(f"THRESHOLD_TECNICO={THRESHOLD_TECNICO}  CONFIDENCE_THRESHOLD_LOW={CONFIDENCE_THRESHOLD_LOW}\n")

    print("Carregando servico ANTES (Nostalgia: 2 frases-lista)...")
    svc_before = CategorizationService(anchors_path=BEFORE_ANCHORS_PATH, enable_mistral_fallback=False)
    print("Carregando servico DEPOIS (Nostalgia: 2 frases reescritas em prosa)...")
    svc_after = CategorizationService(anchors_path=AFTER_ANCHORS_PATH, enable_mistral_fallback=False)

    target_rows = print_table("Casos-alvo (Grupo A)", TARGET_CASES, svc_before, svc_after)

    embedder = SentenceTransformerAdapter()
    anchors_after = json.load(open(AFTER_ANCHORS_PATH, "r", encoding="utf-8"))
    print("\n=== Breakdown por frase individual (estado DEPOIS) - 2 casos-alvo ===")
    phrase_breakdown(embedder, anchors_after, "grão de filme genuíno em retrato quase preto e branco", {"Nostalgia (Analógico)", "Solenidade (Estase)"})
    phrase_breakdown(embedder, anchors_after, "textura de negativo Kodak, tira de contato", {"Nostalgia (Analógico)", "Solenidade (Estase)", "Vitalidade (Ação)"})

    obs_rows = print_table("Caso de observacao (Grupo B, sem forcar)", OBSERVATION_CASE, svc_before, svc_after)
    guard_rows = print_table("Casos de guarda - Solenidade e Vitalidade (Grupo A)", GUARD_CASES, svc_before, svc_after)
    prior_rows = print_table("Checagem cruzada - casos-alvo corrigidos nas rodadas 1-7", PRIOR_ROUNDS_TARGETS, svc_before, svc_after)

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

    def confident_wrong(row):
        a = row["after"]
        return a["top1_anchor"] != row["expected"] and a["top1_score"] >= CONFIDENCE_THRESHOLD_LOW

    print("\n=== CRITERIO DE PARADA ===")
    target_ok = True
    for row in target_rows:
        hit = row["after"]["top1_anchor"] == row["expected"]
        no_confident_wrong = not confident_wrong(row)
        ok = hit or no_confident_wrong
        status = "OK (bateu)" if hit else ("OK (sem erro confiante)" if no_confident_wrong else "FALHOU")
        print(f"  [{status}] {row['text']!r} -> depois top1={row['after']['top1_anchor']} score={row['after']['top1_score']:.3f}")
        target_ok = target_ok and ok

    guard_ok = all(row["after"]["top1_anchor"] == row["expected"] for row in guard_rows)
    prior_ok = all(row["after"]["top1_anchor"] == row["expected"] for row in prior_rows)
    no_group_a_regression_outside_nostalgia = all(r["expected"] == "Nostalgia (Analógico)" for r in regressions)
    no_tecnico_regression = len(tecnico_regressions) == 0

    print(f"\n  2 casos-alvo: {'OK' if target_ok else 'FALHOU'}")
    print(f"  casos de guarda (Solenidade/Vitalidade) sem vazamento: {'OK' if guard_ok else 'FALHOU'}")
    print(f"  checagem cruzada rodadas 1-7: {'OK' if prior_ok else 'FALHOU'}")
    print(f"  Grupo A completo sem divergencia fora de Nostalgia: {'OK' if no_group_a_regression_outside_nostalgia else 'FALHOU'}")
    print(f"  corpus tecnico sem efeito colateral: {'OK' if no_tecnico_regression else 'ALERTA'}")

    success = target_ok and guard_ok and prior_ok and no_group_a_regression_outside_nostalgia and no_tecnico_regression
    print(f"\n  RESULTADO FINAL: {'CRITERIO ATINGIDO' if success else 'CRITERIO NAO ATINGIDO (ver detalhes acima)'}")

    out_path = os.path.join(ROOT, "data", "processed", "r8_comparison.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({
            "threshold_tecnico": THRESHOLD_TECNICO,
            "confidence_threshold_low": CONFIDENCE_THRESHOLD_LOW,
            "target_cases": target_rows,
            "observation_case": obs_rows,
            "guard_cases": guard_rows,
            "prior_rounds_targets": prior_rows,
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
