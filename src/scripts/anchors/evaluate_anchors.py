import sys
import os
import json

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from infrastructure.adapters.sentence_transformer_adapter import SentenceTransformerAdapter

# ── Configuração ────────────────────────────────────────────────────────────────
KNOWLEDGE_JSON = os.path.join(
    os.path.dirname(__file__), "..", "..", "..", "data", "raw", "knowledge_anchors.json"
)

# Queries de teste: texto livre → âncora esperada
TEST_QUERIES = {
    "foto de atleta saltando na luz do sol": "Vitalidade (Ação)",
    "rosto sorridente bem de perto, olhos nítidos": "Conexão (Close-up)",
    "paisagem de montanha com pôr do sol dramático": "Sublime (Paisagem)",
    "retrato corporativo em fundo liso neutro": "Corporativo (Focado)",
    "fest noturna com luzes de neon e pessoas dançando": "Noturno (Festa)",
    "foto antiga com grain e cores desbotadas de polaroid": "Nostalgia (Analógico)",
    "rua suja com multidão confusa e poluição visual": "Conflito (Caos)",
    "corredor vazio, concreto cinza, figura de costas isolada": "Distanciamento (Low-key)",
    "cozinha doméstica com luz natural de janela": "Simplicidade (Cotidiano)",
    "composição simétrica, fundo branco, luz suave equilibrada": "Solenidade (Estase)",
}

# Queries coringas: edge cases com expected=None quando ambíguo, ou com expected quando espera-se resposta clara.
# Categorias: multilíngue, coloquial, vocabulário indireto, armadilha semântica, query curtíssima.
WILDCARD_QUERIES: dict[str, str | None] = {
    # ── Multilíngue ──────────────────────────────────────────────────────────
    "bright mountain landscape at golden hour, tiny human figure": "Sublime (Paisagem)",
    "close portrait, open smile, warm skin tones": "Conexão (Close-up)",
    "dark empty hallway, concrete, no people": "Distanciamento (Low-key)",

    # ── Vocabulário indireto / sem palavras-chave óbvias ─────────────────────
    "pessoa minúscula diante de algo imensurável": "Sublime (Paisagem)",
    "luz vinda de uma janela, café da manhã em casa": "Simplicidade (Cotidiano)",
    "sujeito de costas num lugar deserto": "Distanciamento (Low-key)",
    "instantâneo revelado num laboratório de química fotográfica": "Nostalgia (Analógico)",

    # ── Coloquial / gíria ────────────────────────────────────────────────────
    "vibe lofi, câmera de filme, cores esmaecidas, saudosismo": "Nostalgia (Analógico)",
    "foto bem pesada de rua, tudo bagunçado e sujo": "Conflito (Caos)",
    "galera na balada, todo mundo suado e animado": "Noturno (Festa)",

    # ── Queries curtíssimas (1-2 palavras) ───────────────────────────────────
    "esporte": "Vitalidade (Ação)",      # sem contexto visual
    "caos urbano": "Conflito (Caos)",
    "retrato": None,                     # ambíguo: Conexão vs Corporativo

    # ── Armadilhas semânticas: mistura de duas âncoras ───────────────────────
    "homem de terno sorrindo olhando direto para a câmera": None,   # Corporativo vs Conexão
    "show ao ar livre com público pulando ao sol": None,            # Vitalidade vs Noturno
    "rua abandonada à noite com sombras pesadas": None,             # Distanciamento vs Conflito
    "foto de família dos anos 80 em sala de estar iluminada": None, # Nostalgia vs Simplicidade
    "skatista em trick, postura assimétrica, luz solar dura": "Vitalidade (Ação)",

    # ── Query com ruído / mal formulada ──────────────────────────────────────
    "boa foto, muito bonita, colorida e com pessoas": None,         # deve revelar âncora dominante
    "imagem de algo grande e impressionante lá fora": "Sublime (Paisagem)",
}

SIMILARITY_WARN_THRESHOLD = 0.75  # âncoras acima deste valor são potencialmente redundantes


# ── Carrega JSON ────────────────────────────────────────────────────────────────
def load_knowledge(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# ── Âncora representativa: média dos embeddings por ID ─────────────────────────
def build_anchor_embeddings(data: dict) -> tuple[list[str], np.ndarray]:
    anchor_ids = data["anchors_ids"]
    embeddings = np.array(data["embeddings"])

    unique_ids = list(dict.fromkeys(anchor_ids))  # mantém ordem
    anchor_matrix = []
    for uid in unique_ids:
        idxs = [i for i, a in enumerate(anchor_ids) if a == uid]
        anchor_matrix.append(embeddings[idxs].mean(axis=0))

    return unique_ids, np.array(anchor_matrix)


# ── 1. Heatmap de colisão ───────────────────────────────────────────────────────
def plot_collision_matrix(labels: list[str], matrix: np.ndarray) -> None:
    sim = cosine_similarity(matrix).copy()
    np.fill_diagonal(sim, 0)

    df = pd.DataFrame(sim, index=labels, columns=labels)

    fig, ax = plt.subplots(figsize=(12, 10))
    sns.heatmap(df, annot=True, cmap="coolwarm", fmt=".2f", vmin=0, vmax=1, ax=ax)
    ax.set_title("Matriz de Colisão das Âncoras — Photus-B", fontsize=16)
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()

    out_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "..", "data", "processed", "anchor_collision_matrix.png")
    )
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    fig.savefig(out_path, dpi=150)
    print(f"Heatmap salvo em: {out_path}")
    plt.close(fig)

    # Alertas
    print("\n── Alertas de similaridade alta ──────────────────────────────────────")
    found = False
    for i in range(len(labels)):
        for j in range(i + 1, len(labels)):
            val = sim[i][j]
            if val >= SIMILARITY_WARN_THRESHOLD:
                print(f"  ⚠  {labels[i]}  ↔  {labels[j]}  →  {val:.3f}")
                found = True
    if not found:
        print("  Nenhum par acima do limiar de", SIMILARITY_WARN_THRESHOLD)


# ── 2. Teste de queries ─────────────────────────────────────────────────────────
def run_query_tests(
    labels: list[str],
    anchor_matrix: np.ndarray,
    adapter: SentenceTransformerAdapter,
) -> None:
    print("\n── Teste de Queries ───────────────────────────────────────────────────")
    correct = 0

    for query, expected in TEST_QUERIES.items():
        q_emb = adapter.generate_embeddings(query).reshape(1, -1)
        scores = cosine_similarity(q_emb, anchor_matrix)[0]
        ranked = sorted(zip(labels, scores), key=lambda x: x[1], reverse=True)

        top_label, top_score = ranked[0]
        hit = top_label == expected
        correct += int(hit)

        status = "✓" if hit else "✗"
        print(f"\n  {status} Query: \"{query}\"")
        print(f"     Esperado : {expected}")
        print(f"     Predito  : {top_label}  ({top_score:.3f})")
        if not hit:
            exp_score = next(s for l, s in ranked if l == expected)
            print(f"     Esperado score: {exp_score:.3f}  |  top-3: {[(l, f'{s:.2f}') for l,s in ranked[:3]]}")

    total = len(TEST_QUERIES)
    print(f"\n  Resultado: {correct}/{total} queries corretas ({correct/total*100:.0f}%)")


# ── 3. Teste de queries coringas ────────────────────────────────────────────────
def run_wildcard_tests(
    labels: list[str],
    anchor_matrix: np.ndarray,
    adapter: SentenceTransformerAdapter,
) -> None:
    print("\n── Queries Coringas (edge cases) ──────────────────────────────────────")

    definitive = [q for q, e in WILDCARD_QUERIES.items() if e is not None]
    ambiguous  = [q for q, e in WILDCARD_QUERIES.items() if e is None]
    correct = 0

    for query, expected in WILDCARD_QUERIES.items():
        q_emb = adapter.generate_embeddings(query).reshape(1, -1)
        scores = cosine_similarity(q_emb, anchor_matrix)[0]
        ranked = sorted(zip(labels, scores), key=lambda x: x[1], reverse=True)
        top_label, top_score = ranked[0]
        top3 = [(l, f"{s:.2f}") for l, s in ranked[:3]]

        if expected is None:
            # Ambíguo — apenas observar
            print(f"\n  ? [AMBÍGUO] \"{query}\"")
            print(f"     Top-3 : {top3}")
        else:
            hit = top_label == expected
            correct += int(hit)
            status = "✓" if hit else "✗"
            print(f"\n  {status} [CORINGA] \"{query}\"")
            print(f"     Esperado : {expected}")
            print(f"     Predito  : {top_label}  ({top_score:.3f})")
            if not hit:
                exp_score = next(s for l, s in ranked if l == expected)
                print(f"     Esperado score: {exp_score:.3f}  |  top-3: {top3}")

    total_def = len(definitive)
    total_amb = len(ambiguous)
    print(f"\n  Coringas com resposta esperada : {correct}/{total_def} ({correct/total_def*100:.0f}%)")
    print(f"  Coringas ambíguos (só observar): {total_amb}")


# ── Main ────────────────────────────────────────────────────────────────────────
def main():
    data = load_knowledge(KNOWLEDGE_JSON)
    print(f"JSON carregado: {data['metadata']['total_anchors']} entradas, modelo={data['metadata']['model_name']}")

    labels, anchor_matrix = build_anchor_embeddings(data)
    print(f"Âncoras únicas: {len(labels)} → {labels}")

    adapter = SentenceTransformerAdapter(model_name=data["metadata"]["model_name"])

    plot_collision_matrix(labels, anchor_matrix)
    run_query_tests(labels, anchor_matrix, adapter)
    run_wildcard_tests(labels, anchor_matrix, adapter)


if __name__ == "__main__":
    main()
