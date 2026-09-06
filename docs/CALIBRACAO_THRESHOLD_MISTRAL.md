# Calibração de threshold pra desviar pro Mistral — score_min / gap_min

Só calibração nesta tarefa — a chamada ao Mistral condicionada a score/gap **não foi implementada**.
Objetivo: decidir com dados o critério de quando `CategorizationService` deveria desviar pro Mistral
em vez de confiar no top1 semântico, resolvendo a discrepância da seção 7.2 (metodologia documentada
descreve fast_track/gap; o código implementado, `categorize_text.py`, não tem isso hoje — só a
bifurcação `technical` via regex/`THRESHOLD_TECNICO`).

Estado das âncoras: 55 frases, pós-rodada-8 (`REFINO_NOSTALGIA_R8.md`). Nenhuma frase foi editada
nesta tarefa. Scripts: `scripts/anchors/threshold_sweep.py` (lê
`data/processed/router_health_diag_results.json`, gerado por
`scripts/anchors/diagnose_router_health.py`).

## Passo 1 — Os 46 casos de roteamento semântico (Grupo A + B)

Grupo A (30) + Grupo B (16) = 46 casos. Grupo C (técnico) fica de fora — já tem mecanismo próprio
via regex + `THRESHOLD_TECNICO`. Resultado agregado: **34 corretos, 12 errados** (34/46 = 74% de
acerto top-1 no estado atual, pós-rodada-8).

Os 12 casos errados, ordenados por score decrescente (a tabela completa dos 46 está em
`data/processed/router_health_diag_results.json`):

| Score | Gap | Caso | Esperado | Obtido |
|---|---|---|---|---|
| 0.725 | 0.130 | `pessoa sozinha ao entardecer, sombras longas` | (não deveria ser Distanciamento) | Distanciamento |
| 0.706 | 0.159 | `retrato próximo e emotivo em ambiente de estúdio formal` | Conexão | Corporativo |
| 0.666 | 0.040 | `pessoa em roupa profissional mas em ambiente real, não estúdio` | Simplicidade | Corporativo |
| 0.657 | 0.141 | `show de rock em ambiente escuro` | Noturno | Distanciamento |
| 0.629 | 0.145 | `multidão animada mas com clima positivo, sem tensão` | Vitalidade | Noturno |
| 0.624 | 0.069 | `rosto pequeno e dividido em meio a uma multidão` | Conflito | Conexão |
| 0.622 | 0.069 | `grão de filme genuíno em retrato quase preto e branco` | Nostalgia | Solenidade |
| 0.578 | 0.078 | `estética vintage só que digitalmente perfeita, sem grão real` | (ambíguo/descarte) | Nostalgia |
| 0.568 | 0.110 | `atleta com expressão de dor extrema no rosto` | Conflito | Vitalidade |
| 0.557 | 0.003 | `sobrecarga sensorial, nada no lugar` | Conflito | Solenidade |
| 0.511 | 0.013 | `produto isolado em fundo branco` | Solenidade | `__tecnico__` |
| 0.391 | 0.037 | `pessoa lendo sem posar` | Simplicidade | Distanciamento |

Para referência, a distribuição de gap dos 34 casos **corretos** vai de 0.009 até 0.425 — 23 dos 34
(68%) têm gap abaixo de 0.13, o que já avisa que gap sozinho, em qualquer valor que capture os erros
de gap alto, também vai capturar a maioria dos acertos (ver Passo 2).

## Passo 2 — Sweep de score_min × gap_min

Regra simulada: **se `score < score_min` OU `gap < gap_min` → desvia pro Mistral.** Cenário
otimista (Mistral acerta sempre que é chamado).

### Combinações que mostram o trade-off

| Combinação | score_min | gap_min | Resgatados | Custo | Não resgatados |
|---|---|---|---|---|---|
| score-só, frouxo | 0.45 | 0.00 | 1 | 0 | 11 |
| score-só, moderado | 0.60 | 0.00 | 5 | 9 | 7 |
| **score-só, no cotovelo** | **0.63** | **0.00** | **8** | **11** | **4** |
| score-só, agressivo | 0.70 | 0.00 | 10 | 22 | 2 |
| gap-só, frouxo | 0.00 | 0.05 | 4 | 8 | 8 |
| gap-só, agressivo | 0.00 | 0.10 | 7 | 20 | 5 |
| **score+gap, recomendado** | **0.63** | **0.04** | **9** | **13** | **3** |
| score+gap, agressivo | 0.65 | 0.10 | 9 | 24 | 3 |
| score+gap, extremo | 0.65 | 0.15 | 11 | 28 | 1 |

**Leitura:** gap sozinho é ineficiente — pra capturar os erros de gap mais alto (0.13-0.16), o custo
explode (20-28 acertos desviados à toa) porque boa parte dos acertos também tem gap nessa faixa.
Score sozinho é mais eficiente até um ponto (0.63), onde a curva de custo começa a acelerar mais
rápido que o ganho de resgate (ver fronteira de Pareto abaixo). Combinar os dois com um `gap_min`
pequeno (0.04) captura 1 caso a mais que score sozinho, a um custo marginal baixo (+2).

### Fronteira de Pareto (melhor resgate pra cada nível de custo, sweep fino 0.01)

| Custo | score_min ótimo | gap_min ótimo | Resgatados | Não resgatados |
|---|---|---|---|---|
| 5 | 0.51 | 0.02 | 3 | 9 |
| 9 | 0.59 | 0.00 | 5 | 7 |
| **11** | **0.63** | **0.00** | **8** | **4** |
| **13** | **0.63** | **0.04** | **9** | **3** |
| 19 | 0.66 | 0.04 | 10 | 2 |
| 23 | 0.71 | 0.00 | 11 | 1 |
| 30+ | 0.73+ | 0.10+ | 12 | 0 |

O salto de custo=9 (5 resgatados) pra custo=11 (8 resgatados) é o melhor ganho marginal do sweep
inteiro: **+2 de custo compra +3 resgates**. Depois de custo=13, cada resgate adicional custa cada
vez mais caro (custo=19 pra +1 resgate, custo=23 pra +1, custo=30+ pra o último caso, que é
estruturalmente inatingível sem custo quase total — ver Passo 3).

## Passo 3 — Casos "confiante e errado" (teto estrutural)

No combo recomendado (`score_min=0.63, gap_min=0.04`), **3 casos permanecem não resgatados**:

| Caso | Score | Gap | Esperado | Obtido |
|---|---|---|---|---|
| `pessoa sozinha ao entardecer, sombras longas` | 0.725 | 0.130 | (não deveria ser Distanciamento) | Distanciamento |
| `retrato próximo e emotivo em ambiente de estúdio formal` | 0.706 | 0.159 | Conexão | Corporativo |
| `show de rock em ambiente escuro` | 0.657 | 0.141 | Noturno | Distanciamento |

Note que `"estética vintage só que digitalmente perfeita, sem grão real"` (score 0.578, gap 0.078) —
citado no prompt como candidato ao teto — **é resgatado** no combo recomendado, porque seu score
(0.578) já fica abaixo de `score_min=0.63`. Ele só vira "teto estrutural de verdade" em thresholds
mais frouxos (ex.: `score_min=0.60` não pega, como mostrado no Passo 2). No combo recomendado, ele
já sai da lista de confiante-e-errado.

**O teto estrutural real** (confirmado tentando push score_min/gap_min até os limites testados:
0.75 / 0.17) é composto por 3-4 casos com **score E gap simultaneamente altos** — nenhum dos dois
sinais é fraco o suficiente pra disparar a regra sem também capturar a maioria dos acertos:

- Pra pegar `"pessoa sozinha ao entardecer"` (score 0.725) via score, precisaria `score_min > 0.725`
  — isso captura **26 dos 34 acertos** (76%) como custo.
- Pra pegar `"retrato próximo e emotivo..."` (gap 0.159) via gap, precisaria `gap_min > 0.159` — isso
  captura **25 dos 34 acertos** (74%) como custo.

Esses são os casos que **nenhum threshold de score/gap resolve de forma economicamente viável** —
são erros de vocabulário de âncora (colisão lexical, negação que não funciona em embeddings, mesmo
padrão documentado nas rodadas 2-8), não erros de "baixa confiança" que threshold consegue
sinalizar. Corrigir esses exige mexer nas frases-âncora (rodadas futuras), não no mecanismo de
desvio.

## Passo 4 — Recomendação

**`score_min=0.63, gap_min=0.04`.**

Justificativa:
- Resgata 9 dos 12 erros do corpus (75%), incluindo um caso já documentado como limitação conhecida
  desde a rodada 2 (`"pessoa em roupa profissional mas em ambiente real, não estúdio"` → Corporativo)
  — o `gap_min=0.04` é o que resgata esse caso especificamente (via score isolado ele passava, gap
  0.040 é o que faz a diferença).
- Custo de 13 dos 34 acertos (38%) desviados desnecessariamente pro Mistral — abaixo do ponto onde a
  curva de custo acelera (custo=19+ pra resgatar o próximo caso).
- Está exatamente no início do platô de retornos decrescentes: é o ponto onde o próximo incremento
  de resgate (custo=19 pra +1) já não compensa mais.
- Os 3 casos que sobram como "confiante e errado" são estruturalmente não-resgatáveis por
  score/gap (ver Passo 3) — não há um `score_min`/`gap_min` razoável que os pegue sem custo
  proibitivo, então não vale a pena calibrar mais agressivo só por causa deles.

**Não implementado nesta tarefa** — a mudança em `categorize_text.py` (adicionar a chamada
condicional ao Mistral com esses thresholds) fica pra uma tarefa separada, quando decidido.

## Arquivos gerados

- `scripts/anchors/threshold_sweep.py` — script do sweep, reaproveitável
- `data/processed/threshold_sweep_results.json` — resultados detalhados por combinação testada
- `data/processed/router_health_diag_results.json` — os 51 casos brutos (Grupo A/B/C) usados de base
