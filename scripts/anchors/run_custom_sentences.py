#!/usr/bin/env python3
"""Run custom queries against knowledge anchors and route technical inputs to Mistral."""
import json
import math
import os
import sys
from typing import List, Optional

import typer

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(os.path.join(ROOT, "src"))

from infrastructure.adapters import MistralConnector
from infrastructure.adapters.sentence_transformer_adapter import SentenceTransformerAdapter
from infrastructure.config.prompts.loader import load_prompt
from presentation.cli.terminal import CommandLineInterface
from shared.utils import logger

# ---------------------------------------------------------------------------
# Default sentences used when no --text flag is provided
# ---------------------------------------------------------------------------

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
    "mostre uma cena simples e cotidiana",
]

THRESHOLD_TECNICO = 0.48 

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load_anchors(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def cosine(a: list, b: list) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    return dot / (na * nb) if na and nb else 0.0


def rank_anchors(emb: list, anchors: dict) -> list[dict]:
    """Return anchors deduplicated by anchor_id, sorted by best cosine score."""
    best: dict[str, dict] = {}
    for aid, phrase, aemb in zip(
        anchors.get("anchors_ids", []),
        anchors.get("phrases", []),
        anchors.get("embeddings", []),
    ):
        score = float(cosine(emb, aemb))
        if aid not in best or score > best[aid]["score"]:
            best[aid] = {"anchor_id": aid, "anchor_phrase": phrase, "score": score}
    return sorted(best.values(), key=lambda x: x["score"], reverse=True)


def is_technical(ranked: list[dict]) -> tuple[bool, float]:
    score_tecnico = next(
        (r["score"] for r in ranked if r["anchor_id"] == "__tecnico__"), 0.0
    )
    return score_tecnico >= THRESHOLD_TECNICO, score_tecnico


def call_mistral_technical(connector: MistralConnector, text: str) -> Optional[str]:
    """Send a technical input to Mistral using the technical system prompt."""
    try:
        system_prompt = load_prompt("base")
        # system_promt_two = f"Me responda apenas como ENTENDIDO se o input é tecnico , sem precisar ser no formato JSON"
        messages = [
            {"role": "system", "content": system_prompt},
            # {"role": "system", "content": system_promt_two},
            {"role": "user", "content": text},
        ]
        response = connector.send_message(messages, max_tokens=512, temperature=0.1)
        # magistral models return content as a list of chunks (ThinkChunk, TextChunk, etc.)
        if isinstance(response, list):
            response = "".join(
                chunk.text for chunk in response if hasattr(chunk, "text")
            )
        return str(response) if response is not None else None
    except Exception as e:
        logger.error("Mistral request failed: %s", e)
        return None

# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

app = typer.Typer(help="Run custom sentences against knowledge anchors.")
cli = CommandLineInterface(default_texts=SENTENCES)


@app.command()
def main(
    text: Optional[List[str]] = typer.Option(
        None, "--text", "-t", help="Text to process"
    ),
) -> None:
    anchors_path = os.path.join(ROOT, "data", "raw", "knowledge_anchors.json")
    anchors = load_anchors(anchors_path)

    adapter = SentenceTransformerAdapter()
    mistral = MistralConnector()

    texts = cli.args_text(text)
    embeddings = adapter.generate_embeddings(texts=texts)

    all_results = []

    for sentence, emb in zip(texts, embeddings):
        ranked = rank_anchors(emb, anchors)
        top5 = ranked[:5]
        technical, tech_score = is_technical(ranked)

        # --- display ---
        print("\n---")
        print("Texto:", sentence)
        for r in top5:
            print(f"  - {r['anchor_id']}: {r['score']:.4f}")

        mistral_response = None
        if technical:
            print(f"\n[TÉCNICO detectado — score: {tech_score:.4f}] → roteando para Mistral...")
            mistral_response = call_mistral_technical(mistral, sentence)
            if mistral_response:
                logger.info("Mistral response:\n{}", mistral_response)
                print(mistral_response)
            else:
                print("[ERRO] Mistral não retornou resposta.")

        all_results.append({
            "text": sentence,
            "top": top5,
            "technical": technical,
            "technical_score": tech_score,
            "mistral_response": mistral_response,
        })

    out_path = os.path.join(ROOT, "data", "processed", "custom_sentences_results.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({"results": all_results}, f, ensure_ascii=False, indent=2)

    print("\nResults saved to", out_path)


if __name__ == "__main__":
    app()
