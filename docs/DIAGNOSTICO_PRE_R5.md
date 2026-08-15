# Diagnóstico pré-rodada 5 — Solenidade, Simplicidade, Conflito, Conexão

Só diagnóstico, nenhuma frase-âncora foi editada. Estado do repositório inalterado desde a rodada 4
(`REFINO_CONEXAO_R4.md`): 52 frases, Conexão com 4 (3 originais + a de executivo/rodada 4).

## Passo 1 — Frases atuais das 4 âncoras

**Solenidade (Estase)** — 4 frases:
1. `foto parada e silenciosa`
2. `ambiente organizado, limpo e simétrico`
3. `calmo, sereno, tranquilo, neutro, minimalista, equilibrado, suave`
4. `sem bagunça, sem movimento, tudo no lugar, paz visual, elegante e contido`

**Simplicidade (Cotidiano)** — 4 frases:
1. `foto comum do dia a dia, sem produção`
2. `casa, cozinha, rua, trabalho, rotina`
3. `natural, simples, casual, autêntico, doméstico, familiar, sem pose`
4. `luz de janela, cena ordinária, momento espontâneo, vida real sem filtro`

**Conflito (Caos)** — 4 frases:
1. `foto de confusão e desordem urbana, rua suja e multidão agitada`
2. `cena caótica, tensão`
3. `bagunçado, áspero, agressivo, estressante, poluído, urbano e hostil`
4. `sensação de conflito, ambiente carregado, cena pesada, perturbador visualmente`

**Conexão (Close-up)** — 4 frases:
1. `foto de rosto humano em plano fechado, close extremo, sorriso, olhar direto, expressão emocional`
2. `feliz, alegre, acolhedor, caloroso, amigável, empático, íntimo, carinhoso`
3. `aproximação, afeto, presença humana, emoção no rosto, calor humano`
4. `executivo sorrindo abertamente e à vontade durante a foto, expressão espontânea e descontraída, calor humano mesmo em contexto de trabalho` (adicionada na rodada 4)

## Passo 2 — Breakdown por frase individual nos 2 casos de armadilha

### Caso 1: `"cena doméstica mas visivelmente produzida e estilizada"` (esperado Solenidade, hoje cai em Simplicidade)

| Frase (âncora) | Score |
|---|---|
| Simplicidade: `foto comum do dia a dia, sem produção` | **0.620** ← vence hoje |
| Simplicidade: `luz de janela, cena ordinária, momento espontâneo, vida real sem filtro` | 0.599 |
| Solenidade: `foto parada e silenciosa` | 0.513 |
| Solenidade: `ambiente organizado, limpo e simétrico` | 0.488 |
| Simplicidade: `casa, cozinha, rua, trabalho, rotina` | 0.489 |
| Solenidade: `sem bagunça, sem movimento, tudo no lugar, paz visual, elegante e contido` | 0.465 |
| Simplicidade: `natural, simples, casual, autêntico, doméstico, familiar, sem pose` | 0.378 |
| Solenidade: `calmo, sereno, tranquilo, neutro, minimalista, equilibrado, suave` | 0.264 |

**Achado:** a frase vencedora hoje é `"foto comum do dia a dia, sem produção"` (0.620) — e o texto de
teste contém literalmente **"produzida"**, o oposto semântico de **"sem produção"**. É o mesmo padrão
de negação-não-funciona já documentado na rodada 2 (Corporativo): a raiz lexical `produ-` pesa a
favor da similaridade independente do "sem" na frente. Nenhuma frase de Solenidade contém
vocabulário que capture "estilizada"/"produzida como estética" — a mais próxima
(`"ambiente organizado, limpo e simétrico"`, 0.488) fala de organização espacial, não de produção
fotográfica.

### Caso 2: `"rosto pequeno e disperso em meio a uma multidão"` (esperado Conflito, hoje cai em Conexão)

| Frase (âncora) | Score |
|---|---|
| Conexão: `foto de rosto humano em plano fechado, close extremo, sorriso, olhar direto, expressão emocional` | **0.596** ← vence hoje |
| Conflito: `foto de confusão e desordem urbana, rua suja e multidão agitada` | 0.586 |
| Conflito: `sensação de conflito, ambiente carregado, cena pesada, perturbador visualmente` | 0.471 |
| Conflito: `cena caótica, tensão` | 0.423 |
| Conexão: `aproximação, afeto, presença humana, emoção no rosto, calor humano` | 0.389 |
| Conexão: `executivo sorrindo abertamente e à vontade durante a foto...` (r4) | 0.288 |
| Conflito: `bagunçado, áspero, agressivo, estressante, poluído, urbano e hostil` | 0.279 |
| Conexão: `feliz, alegre, acolhedor, caloroso, amigável, empático, íntimo, carinhoso` | 0.140 |

**Achado:** margem mínima (0.596 vs. 0.586 — 0.010) entre a frase vencedora de Conexão e a melhor de
Conflito. A frase de Conexão vence por compartilhar a palavra **"rosto"** com o texto de teste, mesmo
descrevendo o oposto (`"close extremo"` vs. um rosto pequeno/distante numa multidão). A frase nova da
rodada 4 (`"executivo sorrindo..."`) não é a driver aqui (0.288, bem abaixo) — confirma que a rodada
4 não piorou este caso (consistente com o delta zero já medido no relatório da rodada 4). O
vocabulário de multidão em Conflito já é forte (0.586) — a diferença é pequena o suficiente que
qualquer frase nova em Conflito que reforce "multidão"/"disperso"/"pequeno em meio a" tem chance real
de virar o resultado, mas o risco de colisão é simétrico: Conexão também usa "rosto" como termo
central em sua frase mais forte (0.728 no Grupo A, ver Passo 3), então uma frase nova de Conflito que
mencione "rosto" correria o mesmo risco de sobreposição lexical que aconteceu na rodada 3.

## Passo 3 — Baseline do Grupo A (12 casos centrais × 4 âncoras)

Score **máximo por âncora** (equivalente ao que `rank_anchors` usaria) para cada caso central, contra
as 4 âncoras envolvidas. Célula em negrito = âncora esperada; **⚠** = a âncora esperada não é a que
tem o maior score entre as 4 (risco pré-existente, não causado por nenhuma rodada anterior).

| Caso central | Esperada | Solenidade | Simplicidade | Conflito | Conexão |
|---|---|---|---|---|---|
| `produto isolado em fundo branco` | Solenidade | **0.370** | 0.354 | 0.150 | 0.214 |
| `ambiente minimalista vazio e simétrico` | Solenidade | **0.663** | 0.507 | 0.323 | 0.208 |
| `silêncio visual, nada em movimento` | Solenidade | **0.681** | 0.552 | 0.384 | 0.253 |
| `cozinha iluminada por luz de janela, sem produção` | Simplicidade | 0.358 | **0.432** | 0.116 | 0.137 |
| `pessoa lendo sem posar` | Simplicidade | 0.354 | **0.315** | 0.282 | 0.115 |
| `cena doméstica comum sem drama` | Simplicidade | 0.535 | **0.577** | 0.455 | 0.323 |
| `multidão densa vista de cima` | Conflito | 0.226 | 0.316 | **0.566** | 0.262 |
| `rua com grafite e detritos, tensão visual` | Conflito | 0.298 | 0.366 | **0.721** | 0.264 |
| `sobrecarga sensorial, nada no lugar` | Conflito | **0.557 ⚠** | 0.454 | 0.405 | 0.365 |
| `olhos fechados, luz de contorno, mão tocando o queixo` | Conexão | 0.318 | 0.331 | 0.272 | **0.510** |
| `rosto ocupando o quadro, olhar direto` | Conexão | 0.458 | 0.434 | 0.452 | **0.728** |
| `abraço com rostos próximos em foco` | Conexão | 0.329 | 0.258 | 0.404 | **0.748** |

### Achado não previsto: `"sobrecarga sensorial, nada no lugar"` já está mal-roteado hoje

Este caso central do Grupo A de Conflito (parte do diagnóstico original, não editado em nenhuma
rodada até agora) já perde para Solenidade (0.557 vs. 0.405) **antes de qualquer mudança desta
sessão** — confirmado rodando o serviço completo: top1 atual = Solenidade (0.557), não Conflito.
Causa provável: `"nada no lugar"` no texto de teste vs. `"tudo no lugar"` na frase de Solenidade
(`"sem bagunça, sem movimento, tudo no lugar, paz visual, elegante e contido"`) — mesma família de
problema de negação/superfície lexical dos casos anteriores (`"tudo"` vs. `"nada"` no lugar, polos
opostos, mas a raiz "no lugar" pesa igual). **Isso é uma limitação pré-existente do sistema, não
causada por nenhuma rodada de refino até aqui** — nenhuma âncora de Conflito ou Solenidade foi
tocada nas rodadas 1–4. Fica registrado aqui porque é exatamente o tipo de colisão que o Passo 3
pediu pra mapear antes de escrever qualquer frase nova.

### Riscos de colisão lexical identificados para uma futura correção

- **Simplicidade ↔ Solenidade:** qualquer frase nova de Solenidade que mencione
  "produção"/"produzida"/"estilizada" corre risco de colidir com a frase de Simplicidade
  `"foto comum do dia a dia, sem produção"` (que já vence hoje por sobreposição da raiz "produ-").
  Inversamente, os 2 casos centrais de Simplicidade mais fortes em "doméstico"/"casa"
  (`cena doméstica comum sem drama`, 0.577) já competem de perto com Solenidade (0.535) — margem de
  só 0.042.
- **Conflito ↔ Conexão:** qualquer frase nova de Conflito que mencione "rosto" corre risco de colidir
  com a frase mais forte de Conexão (`"foto de rosto humano em plano fechado..."`, que já domina os 3
  casos centrais de Conexão com 0.510–0.748). O caso central de Conflito mais vulnerável a essa
  colisão seria um hipotético caso que combine "multidão" + "rosto" — não há um assim no Grupo A
  atual, mas o caso de armadilha do Passo 2 (`"rosto pequeno e disperso em meio a uma multidão"`) é
  exatamente essa combinação, e é onde a colisão já acontece.
- **Conflito ↔ Solenidade:** o achado novo (`"sobrecarga sensorial, nada no lugar"`) mostra que
  "nada no lugar" / "tudo no lugar" colidem — uma frase nova de Conflito que use "lugar" ou "ordem"
  correria o mesmo risco de negação de superfície.

## Estado do repositório

Inalterado nesta tarefa — nenhuma frase-âncora foi editada, nenhum embedding foi regenerado. Dados
brutos salvos em `/tmp/breakdown_r5.json` e `/tmp/groupa_baseline_r5.json` (fora do repo, não
versionados) caso precise reprocessar.
