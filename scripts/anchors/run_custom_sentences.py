#!/usr/bin/env python3
"""Run a set of custom example queries against the stored anchors and save results."""
import json
import os
import sys
import math
import typer
from typing import List, Optional


ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(os.path.join(ROOT, "src"))
from infrastructure.adapters.sentence_transformer_adapter import SentenceTransformerAdapter
from presentation.cli.terminal import CommandLineInterface


SENTENCES = [
    "mostre a melhor foto melancolica",
    "mostre a foto com o melhor sorriso",
    "mostre a foto mais artistica",
    "quero um close-up com foco no sorriso",
    "mostre a foto com atmosfera nostálgica",
    "procure a foto mais dramática e contrastada",
    "busque a imagem com cores vibrantes e ação",
    "mostre a paisagem sublime ao pôr do sol",
    "encontre a foto com sensação de isolamento e frieza",
    "mostre uma cena simples e cotidiana"
]



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


app = typer.Typer(help="Run custom sentences against knowledge anchors and save results.")
cli = CommandLineInterface(default_texts=SENTENCES)


@app.command()
def main(text: Optional[List[str]] = typer.Option(None, "--text", "-t", help="Text to process")) -> None:
    anchors_path = os.path.join(ROOT, "data", "raw", "knowledge_anchors.json")
    anchors = load_anchors(anchors_path)

    adapter = SentenceTransformerAdapter()
    texts = cli.args_text(text)
    embs = adapter.generate_embeddings(texts=texts)

    all_results = []
    for text, emb in zip(texts, embs):
        sims = []
        for aid, phrase, aemb in zip(anchors.get('anchors_ids', []), anchors.get('phrases', []), anchors.get('embeddings', [])):
            s = float(cosine(emb, aemb))
            sims.append({'score': s, 'anchor_id': aid, 'anchor_phrase': phrase})
        # deduplicate anchors by anchor_id, keeping the best score per anchor
        best = {}
        for s in sims:
            aid = s['anchor_id']
            if aid not in best or s['score'] > best[aid]['score']:
                best[aid] = s

        unique_sorted = sorted(best.values(), key=lambda x: x['score'], reverse=True)
        top = unique_sorted[:5]

        print('\n---')
        print('Texto:', text)
        for r in top:
            print(f"- {r['anchor_id']}: {r['score']:.4f}")
        all_results.append({'text': text, 'top': top})

    out_path = os.path.join(ROOT, 'data', 'processed', 'custom_sentences_results.json')
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump({'results': all_results}, f, ensure_ascii=False, indent=2)

    print('\nResults saved to', out_path)


if __name__ == '__main__':
    app()
