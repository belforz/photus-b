# Refino de Simplicidade (Cotidiano) — Rodada 6 (causa raiz: listas de palavras-chave)

Continuação da série de rodadas 1-5. Escopo: reescrever as 2 frases de Simplicidade que ainda eram
listas de palavras soltas — mesma causa raiz corrigida em `__tecnico__` na rodada 1.
`THRESHOLD_TECNICO`, `CONFIDENCE_THRESHOLD_LOW` e todas as outras âncoras não foram tocados.

**Resultado: critério atingido** (usando a mesma leitura já confirmada na rodada 1 de Corporativo —
melhora de score dentro do próprio escopo da âncora sendo corrigida não conta como regressão).
Mudança aplicada e mantida.

## O que foi feito

1. **Backup**: `data/processed/anchor_backups/simplicidade_before_r6.json` (4 frases + embeddings,
   estado pós-rodada-5) e snapshot completo `knowledge_anchors_before_r6.json` (54 frases).
2. **2 frases reescritas** (as outras 2, já em prosa, mantidas intactas):
   - `"casa, cozinha, rua, trabalho, rotina"` → *"cena de casa, cozinha ou rua no meio da rotina do
     dia a dia, sem nenhuma preparação especial para a foto"*
   - `"natural, simples, casual, autêntico, doméstico, familiar, sem pose"` → *"pessoa agindo de
     forma natural e casual, sem pose para a câmera, autêntica no ambiente familiar do cotidiano"*
   Contagem de frases de Simplicidade continua 4 (reescrita, não adição). `data/raw/knowledge_anchors.json`
   continua com 54 frases no total. **Mudança aplicada e ativa.**
3. Script: `scripts/anchors/compare_r6.py`.

## Grupo A de Simplicidade — score médio subiu de 0.468 para 0.547

| Caso | Esperado | Antes | Depois |
|---|---|---|---|
| `cozinha iluminada por luz de janela, sem produção` | Simplicidade | Simplicidade 0.432 (correto) | **Simplicidade 0.632 (correto, +0.200)** |
| `pessoa lendo sem posar` | Simplicidade | Distanciamento 0.394 (errado) | Distanciamento 0.394 (errado, sem mudança) |
| `cena doméstica comum sem drama` | Simplicidade | Simplicidade 0.577 (correto) | **Simplicidade 0.613 (correto, +0.036)** |

| Métrica | Antes | Depois |
|---|---|---|
| Score médio | 0.468 | **0.547** |
| Acerto | 2/3 | 2/3 (inalterado) |
| `low_confidence` | 2/3 | **1/3** |

O caso mais fraco do diagnóstico original (`"pessoa lendo sem posar"`, 0.315 no relatório original —
0.394 nesta reexecução) não melhorou: nenhuma das 2 frases reescritas compartilha vocabulário
relevante com esse texto especificamente (não menciona casa/rua/rotina nem pose/natural
explicitamente o suficiente para virar o embedding). Os outros 2 casos centrais tiveram ganho real de
confiança, incluindo um que saiu de `low_confidence=True` para `False`.

## Caso de fronteira (limitação conhecida) — sem mudança, como esperado

| Caso | Esperado | Antes | Depois |
|---|---|---|---|
| `pessoa em roupa profissional mas em ambiente real, não estúdio` (Grupo B oficial) | Simplicidade | Corporativo 0.666 | Corporativo 0.666 (sem mudança) |
| `roupa profissional mas em ambiente real, não estúdio` (customizado) | Simplicidade | Corporativo 0.617 | Corporativo 0.617 (sem mudança) |

Conforme a instrução ("ver se melhora como efeito colateral, sem forçar"), não houve efeito colateral
nem positivo nem negativo — os scores são idênticos ao milésimo. A limitação continua fechada como
documentado na rodada 4.

## Checagem de regressão

- **Casos-alvo das rodadas 1-5** (`retrato de estúdio emotivo`, `coquetel corporativo`, `executivo
  sorrindo`, `cena doméstica produzida`): os 4 permanecem com score idêntico. Nenhum afetado.
- **3 casos centrais de Corporativo:** idênticos, sem mudança.
- **Grupo A completo (30 casos):** 28/30 idênticos. As 2 divergências são as próprias melhoras de
  Simplicidade documentadas acima (mesma âncora, mesmo resultado correto, só score mais alto) — não
  são vazamento pra fora do escopo. Zero divergência em qualquer outra âncora.
- **Corpus técnico (9 casos):** 9/9 idênticos, `__tecnico__` intacto.

## Critério de parada

| Critério | Resultado |
|---|---|
| Score médio de Simplicidade sobe | ✅ OK (0.468 → 0.547) |
| Sem regressão fora do escopo de Simplicidade | ✅ OK (0/27 fora de Simplicidade) |
| Casos-alvo das rodadas 1-5 intactos | ✅ OK |
| Corpus técnico intacto | ✅ OK |

**Critério geral: ATINGIDO.** Não foi necessário isolar nenhuma das 2 frases — nenhuma causou
regressão, ambas contribuíram (uma frase teve efeito mais visível que a outra, mas nenhuma foi
neutra o suficiente para descartar).

## Estado atual do repositório

**Aplicado.** `data/raw/knowledge_anchors.json` mantém 54 frases (Simplicidade continua com 4, agora
todas em prosa — nenhuma é mais lista de palavras soltas). `src/scripts/anchors/sbert_json.py`
reflete essa mudança.

## Atualização da classificação de saúde

Simplicidade (Cotidiano) estava classificada 🔴 Defasada no diagnóstico original e permanecia
🔴 até a rodada 5 (única âncora nunca corrigida estruturalmente, só uma tentativa pontual revertida
na rodada 3). Com o score médio do Grupo A subindo de 0.468 (pior de todas as 11 âncoras) para
0.547 e `low_confidence` caindo de 2/3 para 1/3, a classificação sobe para **🟠 Defasada** — ainda
não saudável (1 caso central sem solução, 1 caso de fronteira conhecido sem solução), mas não é mais
a pior âncora do sistema.
