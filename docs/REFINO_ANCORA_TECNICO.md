# Refino da âncora `__tecnico__` — Passo 4/5/6 (Passo a passo do `prompt_refino_tecnico.md`)

Escopo: só as 9 frases-âncora de `__tecnico__` (`src/scripts/anchors/sbert_json.py`).
`THRESHOLD_TECNICO` (0.48) e `CONFIDENCE_THRESHOLD_LOW` (0.45) **não foram alterados**.

> **Atualização (2ª rodada):** a 1ª versão da reescrita batia no critério de parada em 2/3 frentes
> mas regredia 2 casos do Grupo A (ver seção "1ª rodada" abaixo). Só a frase de iluminação de
> estúdio foi reescrita de novo (equipamento explícito em vez de "luz de estúdio, luz principal e
> de preenchimento" genérico), as outras 7 frases novas não mudaram. **Critério de parada atingido
> na 2ª rodada — ver resultado final logo abaixo.**

## O que foi feito

1. **Backup** (Passo 1): frases + embeddings originais salvos em
   `data/processed/anchor_backups/tecnico_before.json` e
   `data/processed/anchor_backups/knowledge_anchors_before.json` (payload completo das 49 âncoras
   com as 9 antigas de `__tecnico__`, para reprodutibilidade do comparativo).
2. **Reescrita** (Passo 2): as 8 frases de lista de palavras-chave viraram prosa natural (tabela do
   prompt), a 9ª frase (já em prosa) foi mantida sem alteração. Embeddings regenerados com a mesma
   pipeline (`sbert_json.py`, modelo `paraphrase-multilingual-MiniLM-L12-v2`) — `data/raw/knowledge_anchors.json`
   agora reflete a versão nova (**mudança já está live**, ver seção "Estado atual" abaixo).
3. **Corpus de reteste** (Passo 3): Grupo C original (5 casos) + 4 casos novos em prosa não vistos
   no diagnóstico anterior. Script: `scripts/anchors/compare_tecnico_rewrite.py`.

## Tabela comparativa (Passo 4)

| Caso | Score antes | Tech? antes | Score depois | Tech? depois | Top1 depois |
|---|---|---|---|---|---|
| `f/1.8, ISO 800, 1/500s` | 1.000 | True (regex) | 1.000 | True (regex) | `__tecnico__` |
| `deixa o fundo borrado e o rosto nítido` | 0.446 | False | 0.499 | **True** | Conexão (Close-up) |
| `profundidade de campo rasa` | 0.459 | False | 0.671 | **True** | `__tecnico__` |
| `subexposição intencional em low-key` | 0.402 | False | 0.293 | False | Solenidade (Estase) |
| `estoure o brilho dos realces` | 0.432 | False | 0.535 | **True** | Simplicidade (Cotidiano) |
| `quero saber o ajuste de exposição pra não estourar as luzes` **[novo]** | 0.458 | False | 0.806 | **True** | `__tecnico__` |
| `como configuro o ISO pra reduzir ruído na foto` **[novo]** | 0.621 | True | 0.860 | True | `__tecnico__` |
| `deixa o assunto nítido e o fundo totalmente desfocado` **[novo]** | 0.333 | False | 0.390 | False | Distanciamento (Low-key) |
| `ajustar a temperatura de cor pra ficar mais quente` **[novo]** | 0.546 | True | 0.823 | True | `__tecnico__` |

**Resumo:** `technical=True` foi de 3/9 (33%) para 7/9 (78%) no corpus ampliado.

**Erro confiante em âncora errada** (o padrão do diagnóstico original: `technical=False` +
top1 de outra âncora com score ≥ `CONFIDENCE_THRESHOLD_LOW`): existiam **4 casos** antes
(`deixa o fundo borrado...` → Conexão 0.546; `profundidade de campo rasa` → Sublime 0.493;
`estoure o brilho dos realces` → Simplicidade 0.672; `quero saber o ajuste...` → Simplicidade 0.493)
e **0 casos** depois — esse padrão de risco foi eliminado.

Dois casos permanecem sem bater via score semântico:
- `subexposição intencional em low-key` — mesmo sendo o caso de ambiguidade já decidido como
  `technical=True` esperado, o score caiu de 0.402 para 0.293. Não regrediu por causa da reescrita
  em si (já falhava antes), mas a reescrita não resolveu esse caso.
- `deixa o assunto nítido e o fundo totalmente desfocado` — não bateu (0.390), mas também não é um
  erro confiante (top1 Distanciamento 0.418, abaixo do threshold de confiança 0.45).

## 1ª rodada — regressão encontrada no Grupo A

Na 1ª versão da frase de iluminação de estúdio ("luz de estúdio, softbox, luz principal e luz de
preenchimento, montagem de iluminação"), 28/30 casos do Grupo A permaneceram idênticos, mas **2
divergiram:**

| Caso (Grupo A) | Âncora esperada | Antes | Depois (1ª rodada) |
|---|---|---|---|
| `cozinha iluminada por luz de janela, sem produção` | Simplicidade (Cotidiano) | Simplicidade 0.432 | `__tecnico__` 0.578 |
| `iluminação de estúdio limpa, roupa formal` | Corporativo (Focado) | Solenidade 0.512 | `__tecnico__` 0.668 |

Causa: a frase generalizou demais e passou a capturar menções genéricas a "luz"/"iluminação" que
antes eram tratadas como vibe/contexto, não como pedido técnico.

## 2ª rodada — ajuste pontual

Só essa frase foi reescrita, trocando descrição genérica de cena por equipamento técnico explícito
(as outras 7 frases novas + a 9ª mantida não mudaram):

> `"configurar softbox e flash de estúdio, ajustar a potência do strobe e a razão entre luz principal e luz de preenchimento."`

Resultado: **30/30 casos do Grupo A idênticos** (nenhuma divergência) — regressão eliminada sem
perder o ganho nos casos técnicos (permanece 7/9, 0 erros confiantes).

## Critério de parada (Passo 5) — resultado final

| Critério | Resultado |
|---|---|
| Maioria dos casos técnicos roteando como `technical=True` via score semântico | ✅ OK (7/9) |
| Nenhum caso técnico roteado com alta confiança para âncora semântica errada | ✅ OK (0 casos, era 4 antes da reescrita) |
| Zero mudança de comportamento no Grupo A | ✅ OK (30/30 idênticos) |

**Critério geral: ATINGIDO.** Conforme combinado no Passo 5 do prompt, **`THRESHOLD_TECNICO` e
`CONFIDENCE_THRESHOLD_LOW` não foram tocados** — a reescrita de frases sozinha foi suficiente.

## Estado atual do repositório

A reescrita das frases foi aplicada e os embeddings foram regenerados em
`data/raw/knowledge_anchors.json` — a versão nova (2ª rodada) está ativa para qualquer uso de
`CategorizationService` no branch atual. O backup do estado original (antes de qualquer reescrita)
está em `data/processed/anchor_backups/knowledge_anchors_before.json` (drop-in replacement do
arquivo de âncoras) e `data/processed/anchor_backups/sbert_json_before.py.bak` (versão anterior de
`sbert_json.py`), caso seja necessário reverter.

## Casos ainda não resolvidos (fora do critério de parada, não bloqueantes)

Dois casos do corpus técnico continuam sem bater via score semântico, mas nenhum deles é um "erro
confiante" (nenhum foi parar em outra âncora com score ≥ 0.45):
- `subexposição intencional em low-key` (score 0.293) — é o caso de ambiguidade já decidido como
  `technical=True` esperado no prompt original; a reescrita não piorou nem resolveu esse caso.
- `deixa o assunto nítido e o fundo totalmente desfocado` (score 0.390) — top1 é Distanciamento
  (Low-key) com 0.418, abaixo do threshold de confiança.

Ficam registrados para uma eventual próxima rodada, mas não impedem o critério de parada porque a
maioria dos casos técnicos já roteia corretamente e não há erro confiante.
