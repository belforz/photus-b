# Refino da âncora Corporativo (Focado) — Passo 4/5/6/7

Escopo: só Corporativo (Focado). As 3 frases atuais **não foram alteradas** — foram adicionadas
**2 frases novas**. `THRESHOLD_TECNICO`, `CONFIDENCE_THRESHOLD_LOW` e as frases das outras 9 âncoras
(inclusive `__tecnico__`, já refinado) **não foram tocados**.

## O que foi feito

1. **Backup** (Passo 1): `data/processed/anchor_backups/corporativo_before.json` (3 frases +
   embeddings originais) e `data/processed/anchor_backups/knowledge_anchors_before_corporativo.json`
   (snapshot completo das 49 âncoras antes desta rodada — idêntico ao estado final da rodada de
   `__tecnico__`).
2. **2 frases novas** (Passo 2), mantendo as 3 originais intactas:
   - contra vazamento pra Conexão: *"pose formal e distante para estúdio, expressão neutra e
     contida, sem intimidade ou emoção pessoal no olhar"*
   - contra vazamento pra Noturno: *"evento corporativo formal, coquetel ou confraternização de
     trabalho, comportamento sério e comedido, sem euforia nem dança"*
   Embeddings regenerados com a mesma pipeline (`sbert_json.py`) — `data/raw/knowledge_anchors.json`
   agora tem 51 frases (49 → 51). **Mudança já está live.**
3. Script: `scripts/anchors/compare_corporativo_rewrite.py` (mesma abordagem do refino de
   `__tecnico__`, com checagem cruzada extra pro corpus técnico da rodada anterior).

## Tabela comparativa (Passo 4)

### Casos-alvo (critério de aprovação desta rodada)

| Caso | Esperado | Top1 antes | Score antes | Top1 depois | Score depois |
|---|---|---|---|---|---|
| `retrato de estúdio emotivo, com olhar vivo` | Conexão | Conexão | 0.715 | Conexão | 0.715 |
| `cena social mas estática e formal, tipo coquetel corporativo` | Corporativo | **Noturno** | 0.527 | **Corporativo** | 0.655 |

Os 2 casos-alvo bateram: o primeiro já estava correto e continuou (a frase nova não desestabilizou
o que já funcionava); o segundo, que antes vazava pra Noturno, agora acerta Corporativo.

### Caso de observação — Simplicidade (fora de escopo, só registro)

| Caso | Esperado | Top1 antes | Score antes | Top1 depois | Score depois |
|---|---|---|---|---|---|
| `roupa profissional mas em ambiente real, não estúdio` | Simplicidade | Corporativo | 0.480 | Corporativo | **0.617** |

Continua errado (não era critério desta rodada). **Atenção:** o score subiu de 0.480 para 0.617 —
já era um erro confiante antes (≥ 0.45) e continua sendo depois, então pela régua binária
(erro confiante sim/não) não piorou. Mas em termos de magnitude, o erro ficou mais confiante, não
ficou estável. Registro para a 2ª rodada (ataque ao vazamento Corporativo↔Simplicidade), que fica
de fora por decisão já tomada.

### Casos novos — checagem de generalização

| Caso | Esperado | Top1 antes | Score antes | Top1 depois | Score depois |
|---|---|---|---|---|---|
| `sessão de fotos de estúdio com o executivo sorrindo abertamente..., clima descontraído` | Conexão / zona cinzenta | Corporativo | 0.722 | Corporativo | 0.722 (sem mudança) |
| `confraternização de fim de ano da empresa, ambiente sério, brinde protocolar` | Corporativo | Corporativo | 0.384 | Corporativo | 0.448 (melhorou, ainda `low_confidence`) |
| `festa da empresa com a equipe dançando e comemorando` | Noturno | Noturno | 0.654 | Noturno | 0.654 (sem mudança) |

A frase nova 1 (contra Conexão) não generalizou o suficiente para resolver o caso do "executivo
sorrindo, clima descontraído" — continua caindo em Corporativo com score alto e sem mudança
nenhuma (a frase nova simplesmente não superou o score já dominante das 3 frases originais nesse
caso). Não é regressão (nada piorou), mas também não é uma vitória — é um vazamento que a rodada
não teve como alvo direto (o alvo era "retrato de estúdio emotivo, com olhar vivo", que já batia
antes). A frase nova 2 (contra Noturno) não roubou a festa real da empresa — bom sinal de que não
generalizou demais nesse sentido.

## Checagem de regressão — Grupo A completo, 30 casos (Passo 5)

28/30 idênticos. As 2 divergências são, **as duas, dentro do próprio Corporativo**:

| Caso (Grupo A de Corporativo) | Antes | Depois |
|---|---|---|
| `headshot com fundo neutro de estúdio` | **Solenidade** 0.533 | **Corporativo** 0.547 |
| `iluminação de estúdio limpa, roupa formal` | **Solenidade** 0.512 | **Corporativo** 0.552 |

**Achado não previsto no diagnóstico da causa:** o vazamento real dos 2 dos 3 casos centrais de
Corporativo não era pra Conexão nem pra Simplicidade (as duas frentes descritas no contexto) — era
pra **Solenidade (Estase)**. A frase nova 1 ("pose formal e distante... expressão neutra e contida")
puxou o score de Corporativo o suficiente pra virar o jogo nesses 2 casos, mesmo sem ter sido
desenhada pra isso.

**Nenhuma das outras 8 âncoras (27 dos 30 casos fora de Corporativo) mudou.** A checagem cruzada com
o corpus técnico da rodada anterior (9 casos) também deu 9/9 idênticos — `__tecnico__` não foi
afetado.

## Critério de parada (Passo 6) — leitura literal vs. leitura pretendida

Pela letra do critério ("zero mudança de comportamento nos 30 casos do Grupo A, nenhuma âncora, não
só Corporativo"), o resultado é **NÃO atingido**, porque 2 dos 30 casos mudaram — mas os 2 são os
próprios casos centrais de Corporativo virando de errado (Solenidade) pra certo (Corporativo), não
vazamento pra fora do escopo desta rodada. Interpretações possíveis:

| Critério | Leitura literal | Leitura "regressão = vazamento pra fora do escopo" |
|---|---|---|
| 2 casos-alvo do Passo 3 corretos ou sem erro confiante | ✅ OK | ✅ OK |
| Zero mudança nos 30 casos do Grupo A | ❌ FALHOU (2/30) | ✅ OK (0/27 fora de Corporativo; os 2 de dentro são melhora, não vazamento) |
| Caso de observação (Simplicidade) não piorou | ✅ OK (régua binária) | ⚠️ score piorou em magnitude (0.480→0.617), mesmo já sendo erro confiante antes |
| Sem efeito colateral no corpus técnico | ✅ OK | ✅ OK |

Não decidi sozinho qual leitura vale — reportei os dois números brutos e a causa raiz (achado novo:
vazamento real era pra Solenidade, não só Conexão/Simplicidade/Noturno) e a decisão confirmada foi:
**melhora dentro do próprio escopo de Corporativo conta como OK, não como regressão** — os 2 casos
que mudaram são a correção do problema documentado no diagnóstico original (1/3 de acerto), não um
vazamento pra fora da área sob refino. **Critério de parada: ATINGIDO** (leitura "regressão =
vazamento pra fora do escopo").

## Estado atual do repositório

A mudança (2 frases novas) já está aplicada e ativa em `data/raw/knowledge_anchors.json`
(51 frases). Backup do estado anterior (3 frases, sem as 2 novas) em
`data/processed/anchor_backups/knowledge_anchors_before_corporativo.json` e
`data/processed/anchor_backups/sbert_json_before_corporativo.py.bak`, caso seja necessário reverter.

## Pendência registrada (fora de escopo desta rodada)

Vazamento Corporativo↔Simplicidade (`"roupa profissional mas em ambiente real, não estúdio"`, e
possivelmente relacionado, `"cozinha iluminada por luz de janela, sem produção"` já testado no Grupo
A geral) segue sem tratamento, por decisão já tomada no início desta rodada. Fica para uma eventual
2ª rodada de Corporativo, junto com o caso de generalização não resolvido do "executivo sorrindo,
clima descontraído" (que continua confiante em Corporativo em vez de Conexão/zona cinzenta).
