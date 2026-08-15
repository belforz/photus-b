# Reforço de Simplicidade e Conexão — Rodada 3 (Passo 4/5/6/7)

Continuação de `REFINO_ANCORA_CORPORATIVO.md` (rodada 1, sucesso) e
`REFINO_ANCORA_CORPORATIVO_R2.md` (rodada 2, revertida — negação não funciona nessa pipeline).
Escopo desta rodada: **não mexer em Corporativo**; adicionar 1 frase afirmativa em Simplicidade e 1
em Conexão para atacar as 2 pendências que sobraram. `THRESHOLD_TECNICO`,
`CONFIDENCE_THRESHOLD_LOW` e as outras âncoras não foram tocados.

**Resultado: critério NÃO atingido. Revertido**, conforme instruído (não insistir numa 3ª variação).

## O que foi feito

1. **Backup** (Passo 1): `data/processed/anchor_backups/simplicidade_before_r3.json`,
   `conexao_before_r3.json`, e snapshot completo `knowledge_anchors_before_r3.json`.
2. **1 frase nova em cada âncora** (Passo 2), mantendo as existentes intactas:
   - Simplicidade (+1, era 4 → 5): *"pessoa com roupa de trabalho formal em cenário comum do dia a
     dia, mesa de escritório doméstico ou home office improvisado, luz natural de janela"*
   - Conexão (+1, era 3 → 4): *"executivo sorrindo abertamente e à vontade durante a foto, expressão
     espontânea e descontraída, calor humano mesmo em contexto de trabalho"*
   Embeddings regenerados só dessas 2 frases. `data/raw/knowledge_anchors.json` foi a 53 frases
   temporariamente (durante o teste), depois revertido pra 51.
3. Script: `scripts/anchors/compare_r3.py`.

## Tabela comparativa (Passo 4) — casos-alvo

| Caso | Esperado | Antes | Depois |
|---|---|---|---|
| `roupa profissional mas em ambiente real, não estúdio` | Simplicidade | Corporativo 0.617 | **Corporativo 0.617 (sem mudança)** |
| `sessão de fotos de estúdio com o executivo sorrindo..., clima descontraído` | Conexão / zona cinzenta | Corporativo 0.722 | **Conexão 0.865 — corrigido** |

Um dos 2 casos-alvo foi corrigido com folga (Conexão bateu forte, 0.865). O outro **não mudou nem
um milésimo** — investigando por frase individual, a nova frase de Simplicidade chegou a 0.610 pra
esse texto, mas a frase 1 de Corporativo ("pose formal e distante para estúdio...") continuou na
frente por uma margem mínima (0.617 vs 0.610). Quase resolveu, mas não o suficiente.

## Caso de generalização já visto na rodada 2 (falhou lá por causa da negação)

| Caso | Esperado | Antes | Depois |
|---|---|---|---|
| `empresário posando para revista, ambiente de escritório real, sem produção de estúdio` | Simplicidade / zona cinzenta | Corporativo 0.478 | **Simplicidade 0.559 — corrigido** |

A abordagem afirmativa (sem negação) resolveu esse caso, que a rodada 2 tinha piorado.

## Regressão real encontrada — Grupo A de Corporativo

| Caso (Grupo A de Corporativo) | Antes | Depois |
|---|---|---|
| `iluminação de estúdio limpa, roupa formal` | Corporativo 0.552 (correto) | **Simplicidade 0.721 (errado)** |

**Causa raiz identificada:** a nova frase de Simplicidade contém literalmente "roupa de trabalho
formal" — esse texto de teste também contém "roupa formal". A sobreposição lexical direta
("roupa formal") dominou o score (0.721) e vazou um caso central de Corporativo (que a rodada 1
tinha corrigido) de volta pra Simplicidade. Isso é um efeito colateral clássico de mean pooling:
frases que compartilham um n-grama saliente ("roupa formal") colam entre si mesmo quando o resto do
contexto (estúdio vs. casa) devia diferenciar.

Esse caso está no Grupo A original do diagnóstico (um dos 3 casos centrais de Corporativo) — é
exatamente o tipo de regressão que os Passos 5 pedem pra reportar sem tentar corrigir sozinho.

## Casos de guarda (Passo 3) — 2 alarmes, mas achado importante: são falsos positivos desta rodada

| Caso | Esperado | Antes | Depois |
|---|---|---|---|
| `foto de perfil para o site da empresa, sorriso discreto, fundo neutro de estúdio` | Corporativo | Corporativo 0.712 | Corporativo 0.712 ✅ sem mudança |
| `cena doméstica mas visivelmente produzida e estilizada` | Solenidade | **Simplicidade 0.620** | **Simplicidade 0.620** ⚠️ sem mudança |
| `rosto pequeno e disperso em meio a uma multidão` | Conflito | **Conexão 0.596** | **Conexão 0.596** ⚠️ sem mudança |
| `retrato de estúdio emotivo, com olhar vivo` | Conexão | Conexão 0.715 | Conexão 0.715 ✅ sem mudança |
| `cena social mas estática e formal, tipo coquetel corporativo` | Corporativo | Corporativo 0.655 | Corporativo 0.655 ✅ sem mudança |

Os 2 casos marcados ⚠️ já estavam errados **antes** da rodada 3, com o **score idêntico** antes e
depois (até a 3ª casa decimal) — ou seja, as frases novas desta rodada tiveram efeito **zero** nesses
2 casos; não foi a mudança que causou o desvio. São, na prática, variações dos casos de armadilha já
catalogados no Grupo B do diagnóstico original (`"cena doméstica mas visivelmente produzida e
estilizada"` → trap Simplicidade; `"rosto pequeno e dividido em meio a uma multidão"` → trap
Conexão) — **limitações pré-existentes, não relacionadas a esta rodada**, e ficam fora do escopo
aqui.

## Checagem de regressão completa (Passo 5)

- **Grupo A completo (30 casos):** 29/30 idênticos. 1 divergência real: `iluminação de estúdio
  limpa, roupa formal` (ver seção acima).
- **Corpus técnico (9 casos):** 9/9 idênticos, `__tecnico__` intacto.
- Os outros 2 casos centrais de Corporativo (`headshot com fundo neutro de estúdio`,
  `foto que colocaria no LinkedIn sem hesitar`) permaneceram corretos e sem mudança de score.

## Critério de parada (Passo 6)

| Critério | Resultado |
|---|---|
| 2 casos-alvo corrigidos (ou sem erro confiante) | ❌ FALHOU (1/2: só o caso de Conexão) |
| Casos de guarda sem vazamento causado por esta rodada | ⚠️ 2 alarmes, mas ambos pré-existentes (score inalterado) — não causados por esta rodada |
| 3 casos centrais de Corporativo continuam corretos | ❌ **FALHOU** (1/3 regrediu: `iluminação de estúdio limpa, roupa formal`) |
| Grupo A completo sem divergência | ❌ FALHOU (1/30, é a mesma regressão acima) |
| Corpus técnico sem efeito colateral | ✅ OK |

**Critério geral: NÃO atingido**, por causa da regressão real em Corporativo causada pela
sobreposição lexical "roupa formal" entre a nova frase de Simplicidade e um caso central de
Corporativo. Conforme instruído, **não tentei uma 3ª variação da mesma frase — revertido**.

## Estado atual do repositório

**Revertido.** `data/raw/knowledge_anchors.json` e `src/scripts/anchors/sbert_json.py` restaurados a
partir de `data/processed/anchor_backups/knowledge_anchors_before_r3.json` e
`sbert_json_before_r3.py.bak` — de volta ao estado pós-rodada-1 de Corporativo (51 frases:
Simplicidade com 4, Conexão com 3, Corporativo com 5). `THRESHOLD_TECNICO`,
`CONFIDENCE_THRESHOLD_LOW` e todas as outras âncoras seguem intocadas durante toda a sessão de
refino (rodadas 1–3).

## Resumo do que ficou registrado como limitação conhecida (não forçado)

- `"roupa profissional mas em ambiente real, não estúdio"` → cai em Corporativo (0.617), por uma
  margem de 0.007 sobre a melhor tentativa de correção testada. Fica registrado como limitação
  conhecida — forçar mais pode reintroduzir a regressão vista nesta rodada (sobreposição lexical
  "roupa formal" com casos legítimos de Corporativo).
- `"empresário posando para revista, ambiente de escritório real, sem produção de estúdio"` →
  mesma família de caso, mesma tensão.
- `"cena doméstica mas visivelmente produzida e estilizada"` (→ Simplicidade em vez de Solenidade) e
  `"rosto pequeno e disperso em meio a uma multidão"` (→ Conexão em vez de Conflito) — achados novos,
  não causados por esta rodada, correspondem aos casos de armadilha já conhecidos do Grupo B do
  diagnóstico original. Ficam registrados como pendência separada, fora do escopo de Corporativo.
- `"sessão de fotos de estúdio com o executivo sorrindo abertamente..., clima descontraído"` — **este
  foi resolvido** nesta rodada (Conexão 0.865), mas como o critério geral falhou por causa da
  regressão em Corporativo, a rodada inteira foi revertida, então essa correção específica **não
  está mais ativa** no repositório. Fica documentada aqui como a abordagem que funcionou, caso uma
  eventual rodada 4 queira reaproveitar só a frase de Conexão sem a de Simplicidade.
