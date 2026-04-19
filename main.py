import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "src"))
from infrastructure.adapters.sentence_transformer_adapter import SentenceTransformerAdapter


def _format_embedding(embed, preview_len: int = 8) -> str:
    try:
        vals = list(embed)
    except Exception:
        vals = embed
    total = len(vals)
    preview = ", ".join(f"{v:.6f}" for v in vals[:preview_len])
    suffix = ", ..." if total > preview_len else ""
    return f"[{preview}{suffix}] (len={total})"


def main():
    connector = SentenceTransformerAdapter()

    sentences = [
        "mostre a melhor foto melancolica",
    ]

    try:
        embeddings = connector.generate_embeddings(texts=sentences)
    except Exception as e:
        print("Erro ao gerar embeddings:", e)
        return

    for text, emb in zip(sentences, embeddings):
        print("Texto:", text)
        print("Embedding preview:", _format_embedding(emb))
        print()


if __name__ == "__main__":
    main()
