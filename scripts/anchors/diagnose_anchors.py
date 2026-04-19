#!/usr/bin/env python3
import json
import os
import sys
import math

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))


def load_anchors(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def compute_stats(emb):
    vals = [float(x) for x in emb]
    n = len(vals)
    mean = sum(vals) / n if n else 0.0
    var = sum((x - mean) ** 2 for x in vals) / n if n else 0.0
    std = math.sqrt(var)
    norm = math.sqrt(sum(x * x for x in vals))
    mn = min(vals) if n else 0.0
    mx = max(vals) if n else 0.0
    any_nan = any(math.isnan(x) for x in vals)
    return {
        "len": n,
        "mean": mean,
        "std": std,
        "norm": norm,
        "min": mn,
        "max": mx,
        "any_nan": any_nan,
    }


def flag_issue(stats, expected_dim, zero_norm_thresh=1e-8, low_std_thresh=1e-6):
    issues = []
    if stats["len"] != expected_dim:
        issues.append(f"wrong_dim({stats['len']})")
    if stats["any_nan"]:
        issues.append("nan")
    if stats["norm"] <= zero_norm_thresh:
        issues.append(f"zero_norm({stats['norm']:.3e})")
    if stats["std"] <= low_std_thresh:
        issues.append(f"low_std({stats['std']:.3e})")
    return issues


def main():
    anchors_path = os.path.join(ROOT, "data", "raw", "knowledge_anchors.json")
    if not os.path.exists(anchors_path):
        print("Anchors file not found:", anchors_path)
        sys.exit(1)

    data = load_anchors(anchors_path)
    expected_dim = data.get("metadata", {}).get("vector_dimension", None)
    embeddings = data.get("embeddings", [])
    ids = data.get("anchors_ids", [])
    phrases = data.get("phrases", [])

    results = []
    totals = {"checked": 0, "nan": 0, "zero_norm": 0, "wrong_dim": 0, "low_std": 0}

    for i, emb in enumerate(embeddings):
        aid = ids[i] if i < len(ids) else f"anchor_{i}"
        phrase = phrases[i] if i < len(phrases) else ""
        stats = compute_stats(emb)
        issues = flag_issue(stats, expected_dim if expected_dim is not None else stats["len"]) 
        results.append({"id": aid, "phrase": phrase, "stats": stats, "issues": issues})

        totals["checked"] += 1
        if any("nan" in it for it in issues):
            totals["nan"] += 1
        if any(it.startswith("zero_norm") for it in issues):
            totals["zero_norm"] += 1
        if any(it.startswith("wrong_dim") for it in issues):
            totals["wrong_dim"] += 1
        if any(it.startswith("low_std") for it in issues):
            totals["low_std"] += 1

    # Print summary
    print("Anchors diagnostic summary")
    print("-------------------------")
    print(f"Checked: {totals['checked']}")
    print(f"NaN embeddings: {totals['nan']}")
    print(f"Zero-norm embeddings: {totals['zero_norm']}")
    print(f"Wrong-dimension embeddings: {totals['wrong_dim']}")
    print(f"Very low std embeddings: {totals['low_std']}")
    print()

    # Print detailed list of any issues
    any_issues = [r for r in results if r["issues"]]
    if any_issues:
        print("Anchors with issues:")
        for r in any_issues:
            s = r["stats"]
            print(f"- {r['id']}: issues={r['issues']}, len={s['len']}, norm={s['norm']:.4f}, mean={s['mean']:.4g}, std={s['std']:.4g}")
    else:
        print("No issues detected in anchors embeddings.")

    # Save results
    out_path = os.path.join(ROOT, "data", "processed", "anchors", "diagnose_results.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({"summary": totals, "results": results}, f, ensure_ascii=False, indent=2)

    print() 
    print("Detailed results written to:", out_path)


if __name__ == "__main__":
    main()
