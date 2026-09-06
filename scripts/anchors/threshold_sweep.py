#!/usr/bin/env python3
"""Sweep de score_min x gap_min pra calibrar quando desviar pro Mistral em vez
de confiar no top1 semantico (Passo 2/3/4 do prompt de calibracao).

Regra simulada: se score_top1 < score_min OU gap < gap_min -> desvia pro
Mistral. Cenario otimista: assume que o Mistral acerta sempre que e chamado.

So le os 46 casos (Grupo A + Grupo B) de
data/processed/router_health_diag_results.json - nao chama o roteador de
novo, nao edita nenhuma ancora.
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
RESULTS_PATH = os.path.join(ROOT, "data", "processed", "router_health_diag_results.json")


def load_cases():
    rows = json.load(open(RESULTS_PATH, "r", encoding="utf-8"))
    return [r for r in rows if r["group"] in ("A", "B")]


def simulate(cases, score_min, gap_min):
    resgatados = []
    custo = []
    nao_resgatados_correto = []  # eram corretos e continuam nao desviados (bom, sem custo)
    for c in cases:
        score = c["top1_score"]
        gap = c["gap"] if c["gap"] is not None else 0.0
        desvia = (score < score_min) or (gap < gap_min)
        correto = c["hit_expected"]
        if desvia and not correto:
            resgatados.append(c)
        elif desvia and correto:
            custo.append(c)
        elif not desvia and not correto:
            nao_resgatados_correto.append(c)  # confiante e errado
    return resgatados, custo, nao_resgatados_correto


def main():
    cases = load_cases()
    total = len(cases)
    total_errados = sum(1 for c in cases if not c["hit_expected"])
    total_corretos = total - total_errados
    print(f"Total de casos (Grupo A+B): {total} ({total_corretos} corretos, {total_errados} errados)\n")

    combos = [
        ("score-so, frouxo", 0.45, 0.0),
        ("score-so, agressivo", 0.60, 0.0),
        ("score-so, muito agressivo", 0.70, 0.0),
        ("gap-so, frouxo", 0.0, 0.05),
        ("gap-so, agressivo", 0.0, 0.10),
        ("score+gap, moderado", 0.50, 0.08),
        ("score+gap, agressivo", 0.55, 0.10),
        ("score+gap, muito agressivo", 0.60, 0.12),
        ("score+gap, extremo", 0.65, 0.15),
    ]

    print(f"{'Combinacao':<28} {'score_min':>9} {'gap_min':>8} {'resgatados':>11} {'custo':>7} {'nao_resgatados':>15}")
    print("-" * 85)
    results = {}
    for name, score_min, gap_min in combos:
        resgatados, custo, nao_resg = simulate(cases, score_min, gap_min)
        results[(score_min, gap_min)] = (resgatados, custo, nao_resg)
        print(f"{name:<28} {score_min:>9.2f} {gap_min:>8.2f} {len(resgatados):>11} {len(custo):>7} {len(nao_resg):>15}")

    # full sweep pra achar a fronteira de pareto (score_min 0.40-0.70 passo 0.05, gap_min 0.02-0.15 passo 0.01)
    print("\n=== Sweep completo (score_min 0.40-0.70 x gap_min 0.02-0.15) - so combinacoes na fronteira ===")
    full_results = []
    sm = 0.40
    while sm <= 0.70 + 1e-9:
        gm = 0.02
        while gm <= 0.15 + 1e-9:
            resgatados, custo, nao_resg = simulate(cases, round(sm, 2), round(gm, 2))
            full_results.append((round(sm, 2), round(gm, 2), len(resgatados), len(custo), len(nao_resg)))
            gm += 0.01
        sm += 0.05

    # fronteira de pareto: pra cada nivel de custo, o maior resgate
    from collections import defaultdict
    best_by_custo = {}
    for sm, gm, resg, custo, nao_resg in full_results:
        key = custo
        if key not in best_by_custo or resg > best_by_custo[key][2]:
            best_by_custo[key] = (sm, gm, resg, nao_resg)
    print(f"{'custo':>6} {'melhor score_min':>17} {'melhor gap_min':>15} {'resgatados':>11} {'nao_resgatados':>15}")
    for custo in sorted(best_by_custo):
        sm, gm, resg, nao_resg = best_by_custo[custo]
        print(f"{custo:>6} {sm:>17.2f} {gm:>15.2f} {resg:>11} {nao_resg:>15}")

    # Passo 3: casos "confiante e errado" no threshold mais agressivo testado
    print("\n=== Passo 3: casos 'confiante e errado' (nao resgatados mesmo no mais agressivo: score_min=0.65, gap_min=0.15) ===")
    _, _, nao_resg_extremo = simulate(cases, 0.65, 0.15)
    for c in nao_resg_extremo:
        print(f"  [{c['group']}] {c['text']!r}")
        print(f"      esperado={c['expected_anchor']} obtido={c['top1_anchor']} score={c['top1_score']:.3f} gap={c['gap']:.3f}")

    out_path = os.path.join(ROOT, "data", "processed", "threshold_sweep_results.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({
            "total_cases": total,
            "total_corretos": total_corretos,
            "total_errados": total_errados,
            "combos": [
                {
                    "name": name, "score_min": sm, "gap_min": gm,
                    "resgatados": [c["text"] for c in results[(sm, gm)][0]],
                    "custo": [c["text"] for c in results[(sm, gm)][1]],
                    "nao_resgatados": [c["text"] for c in results[(sm, gm)][2]],
                }
                for name, sm, gm in combos
            ],
            "casos_confiante_errado_extremo": [
                {"text": c["text"], "expected": c["expected_anchor"], "top1": c["top1_anchor"], "score": c["top1_score"], "gap": c["gap"]}
                for c in nao_resg_extremo
            ],
        }, f, ensure_ascii=False, indent=2)
    print(f"\nResultados salvos em: {out_path}")


if __name__ == "__main__":
    main()
