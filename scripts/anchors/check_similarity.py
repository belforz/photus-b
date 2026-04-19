
#!/usr/bin/env python3
import json
import os
import sys
import math

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(os.path.join(ROOT, "src"))

from infrastructure.adapters.sentence_transformer_adapter import SentenceTransformerAdapter


def cosine(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


def load_anchors(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    if len(sys.argv) < 2:
        print("Usage: check_similarity.py \"sua frase\"")
        sys.exit(1)

    text = sys.argv[1]
    anchors_path = os.path.join(ROOT, "data", "raw", "knowledge_anchors.json")
    anchors = load_anchors(anchors_path)

    adapter = SentenceTransformerAdapter()
    emb = adapter.generate_embeddings(texts=[text])[0]

    sims = []
    for aid, phrase, aemb in zip(anchors.get("anchors_ids", []), anchors.get("phrases", []), anchors.get("embeddings", [])):
        s = cosine(emb, aemb)
        sims.append((s, aid, phrase))

    sims.sort(reverse=True, key=lambda x: x[0])

    print(f"Frase: {text}\n")
    print("Top similar anchors:")
    for score, aid, phrase in sims[:5]:
        print(f"- {aid}: {score:.4f} — {phrase}")


if __name__ == "__main__":
    main()
