# Reforço de Conexão — Rodada 4 (Passo 4/5/6/7)

Continuação de `REFINO_SIMPLICIDADE_CONEXAO_R3.md` (rodada 3, revertida — a frase de Simplicidade
causou regressão em Corporativo por sobreposição lexical de "roupa formal"). Esta rodada isola só a
parte que funcionou na rodada 3: a frase de Conexão, sozinha. `THRESHOLD_TECNICO`,
`CONFIDENCE_THRESHOLD_LOW`, Simplicidade, Corporativo e as demais âncoras não foram tocados.

**Resultado: critério ATINGIDO. Mudança aplicada e mantida.**

## O que foi feito

1. **Backup** (Passo 1): confirmado estado de partida = pós-rodada-1 de Corporativo (51 frases:
   Simplicidade 4, Conexão 3, Corporativo 5 — o mesmo estado em que a rodada 3 foi revertida).
   Backup em `data/processed/anchor_backups/conexao_before_r4.json` e
   `knowledge_anchors_before_r4.json`.
2. **1 frase nova só em Conexão** (Passo 2), mantendo as 3 existentes e todas as outras âncoras
   intactas: *"executivo sorrindo abertamente e à vontade durante a foto, expressão espontânea e
   descontraída, calor humano mesmo em contexto de trabalho"*. `data/raw/knowledge_anchors.json`
   foi de 51 para 52 frases. **Mudança aplicada e ativa.**
3. Script: `scripts/anchors/compare_r4.py`.

## Tabela comparativa (Passo 4)

| Caso | Esperado | Antes | Depois |
|---|---|---|---|
| `sessão de fotos de estúdio com o executivo sorrindo..., clima descontraído` | Conexão | Corporativo 0.722 | **Conexão 0.865 ✅** |

Corrigido com folga — mesmo resultado da rodada 3, isolado da frase de Simplicidade.

### Checagem específica: a regressão da rodada 3 não reapareceu

| Caso | Esperado | Antes | Depois |
|---|---|---|---|
| `iluminação de estúdio limpa, roupa formal` | Corporativo | Corporativo 0.552 | **Corporativo 0.552 ✅ (score idêntico)** |

Confirma a causa raiz apontada na rodada 3: a regressão vinha exclusivamente da frase de
Simplicidade (sobreposição lexical "roupa formal"), não da frase de Conexão. Sem essa frase, o caso
central de Corporativo nem se move um milésimo.

## Casos de guarda (Passo 3) — efeito cirúrgico, delta zero em todos

| Caso | Esperado | Antes | Depois | Delta |
|---|---|---|---|---|
| `foto de perfil para o site da empresa, sorriso discreto, fundo neutro de estúdio` | Corporativo | Corporativo 0.712 | Corporativo 0.712 | +0.000 |
| `cena doméstica mas visivelmente produzida e estilizada` | Solenidade | Simplicidade 0.620 | Simplicidade 0.620 | +0.000 |
| `rosto pequeno e disperso em meio a uma multidão` | Conflito | Conexão 0.596 | Conexão 0.596 | +0.000 |
| `retrato de estúdio emotivo, com olhar vivo` | Conexão | Conexão 0.715 | Conexão 0.715 | +0.000 |
| `cena social mas estática e formal, tipo coquetel corporativo` | Corporativo | Corporativo 0.655 | Corporativo 0.655 | +0.000 |

Notável: mesmo o caso de guarda que envolvia risco explícito de piora (`"rosto pequeno e disperso em
meio a uma multidão"`, que já vazava pra Conexão e poderia piorar com a nova frase falando em "calor
humano") **não mudou nem um milésimo**. A frase nova não teve nenhum efeito colateral mensurável em
nenhum dos 5 casos de guarda — o resultado mais limpo de todas as 4 rodadas desta série.

## Checagem de regressão completa (Passo 5)

- **Grupo A completo (30 casos):** **30/30 idênticos** — zero divergência, em qualquer âncora.
- **3 casos centrais de Corporativo:** todos corretos, todos com score idêntico ao pós-rodada-1.
- **Corpus técnico (9 casos):** 9/9 idênticos, `__tecnico__` intacto.

## Critério de parada (Passo 6)

| Critério | Resultado |
|---|---|
| Caso-alvo roteando pra Conexão (ou fora de Corporativo com score alto) | ✅ OK — bateu em cheio (0.865) |
| Regressão da rodada 3 (`iluminação de estúdio...`) ausente | ✅ OK — score idêntico |
| Grupo A, casos centrais de Corporativo, corpus técnico sem divergência nova | ✅ OK — 30/30 + 9/9 idênticos |
| Casos de guarda não pioraram | ✅ OK — delta zero nos 5 |

**Critério geral: ATINGIDO em todas as frentes.** Mudança fica aplicada.

## Estado atual do repositório

**Aplicado.** `data/raw/knowledge_anchors.json` tem 52 frases (Simplicidade 4, Conexão **4**,
Corporativo 5, `__tecnico__` 9, demais inalteradas). `src/scripts/anchors/sbert_json.py` reflete essa
mudança. Nada foi revertido nesta rodada.

## Fechamento formal: `"roupa profissional mas em ambiente real, não estúdio"` — limitação conhecida

Por decisão já tomada no início desta rodada, este caso **não é mais tratado como pendência em
aberto** — passa a ser registrado como limitação conhecida do sistema. Duas abordagens distintas já
foram tentadas e ambas falharam por motivos estruturais diferentes:

1. **Rodada 2 (negação):** reescrever a frase de Corporativo com cláusula de exclusão ("sem ambiente
   doméstico"). Falhou porque modelos de sentence-embedding com mean pooling não tratam negação de
   forma confiável — a presença lexical do termo negado ainda conta a favor da similaridade,
   independente do "sem" na frente. O erro **piorou** (0.617 → 0.649).
2. **Rodada 3 (frase afirmativa em Simplicidade):** descrever o caso-alvo diretamente, sem negar
   nada. Chegou perto (Simplicidade 0.610 vs. Corporativo 0.617 — margem de 0.007) mas não superou,
   e a mesma frase causou uma regressão real num caso central de Corporativo por sobreposição
   lexical direta ("roupa formal" aparece em ambos os textos).

Ambas as tentativas esbarraram na mesma tensão de fundo: o texto do caso (`"roupa profissional...
não estúdio"`) e o caso central de Corporativo que não pode regredir (`"iluminação de estúdio...
roupa formal"`) compartilham vocabulário de superfície ("roupa formal") que o modelo de embedding
usa como sinal forte de similaridade, independente da distinção semântica pretendida (estúdio vs.
ambiente real). Não há uma frase-âncora simples que resolva isso sem reintroduzir a regressão — seria
necessário uma abordagem estrutural diferente (ex.: heurística extra fora do ranking por cosseno,
fora do escopo de "refinar frases de âncora"). Fica registrado como limitação conhecida, sem mais
tentativas nesta série de refino.
