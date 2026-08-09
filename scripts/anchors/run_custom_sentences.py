#!/usr/bin/env python3
"""Run custom queries against knowledge anchors and export routing categories."""
import json
import os
import sys
from typing import Any, List, Optional

import typer

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(os.path.join(ROOT, "src"))

from domain.application.use_cases import CategorizationService
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
    category_out: str = typer.Option(
        os.path.join(ROOT, "data", "processed", "category_payload.json"),
        "--category-out",
        "-c",
        help="Output JSON file for downstream category payload.",
    ),
) -> None:
    anchors_path = os.path.join(ROOT, "data", "raw", "knowledge_anchors.json")
    service = CategorizationService(anchors_path=anchors_path)

    texts = cli.args_text(text)
    if not texts:
        prompt_text = typer.prompt("Digite uma frase para categorizar")
        texts = [prompt_text]

    all_results = []
    category_payloads = []

    for sentence in texts:
        result = service.categorize(sentence, top_k=5)

        # --- display ---
        print("\n---")
        print("Texto:", sentence)
        for m in result.top_matches:
            print(f"  - {m.anchor_id}: {m.score:.4f}")

        if result.technical:
            print(f"\n[TÉCNICO detectado — score: {result.technical_score:.4f}] → roteando para Mistral...")
            logger.info("Sending to Mistral: %s", sentence)
            if result.mistral_response:
                logger.info("Mistral response:\n%s", result.mistral_response)
                print(f"Resposta Mistral:\n{result.mistral_response}")
            else:
                print("[AVISO] Mistral não retornou resposta. Verifique logs para detalhes.")
        else:
            print(f"[Não-técnico] score: {result.technical_score:.4f} (limiar: {result.threshold})")

        all_results.append({
            "text": sentence,
            "top": [m.to_dict() for m in result.top_matches],
            "technical": result.technical,
            "technical_score": result.technical_score,
            "mistral_response": result.mistral_response,
        })

        category_payloads.append(result.to_category_payload())

    out_path = os.path.join(ROOT, "data", "processed", "custom_sentences_results.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({"results": all_results}, f, ensure_ascii=False, indent=2)

    category_export: dict[str, Any]
    if len(category_payloads) == 1:
        category_export = category_payloads[0]
    else:
        category_export = {"items": category_payloads}

    with open(category_out, "w", encoding="utf-8") as f:
        json.dump(category_export, f, ensure_ascii=False, indent=2)

    print("\nResults saved to", out_path)
    print("Category payload saved to", category_out)


if __name__ == "__main__":
    app()
