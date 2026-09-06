# Refino de Nostalgia (Analógico) — Rodada 8

Continuação de `DIAGNOSTICO_PRE_R8_NOSTALGIA.md` e da série de rodadas 1-7. Escopo: reescrever 2 das
6 frases de Nostalgia (as 4 restantes intactas). `THRESHOLD_TECNICO`, `CONFIDENCE_THRESHOLD_LOW` e
todas as outras âncoras não foram tocados.

**Resultado: parcialmente atingido.** 1 das 2 frases causou uma regressão real num caso central de
Corporativo (já corrigido na rodada 1) e foi isolada/revertida; a outra ficou e resolveu seu
caso-alvo com folga.

## O que foi feito

1. **Backup**: `data/processed/anchor_backups/nostalgia_before_r8.json` (6 frases + embeddings,
   estado pós-rodada-7) e snapshot completo `knowledge_anchors_before_r8.json` (55 frases).
2. **2 frases reescritas** (as outras 4 mantidas intactas):
   - `"película, polaroid, filme de 35mm"` → *"retrato com grão de filme genuíno e visível, tons
     quase em preto e branco, textura autêntica de negativo fotográfico revelado quimicamente"*
   - `"saudade, memória, passado, afeto antigo, estética analógica, revelado à mão"` → *"textura de
     negativo de filme Kodak, tira de contato com marcas e arranhões do processo de revelação
     química, imperfeições autênticas de laboratório analógico"*

## Rodada inicial (2 frases juntas) — resultado misto

| Caso-alvo | Esperado | Antes | Depois (2 frases) |
|---|---|---|---|
| `grão de filme genuíno em retrato quase preto e branco` | Nostalgia | Solenidade 0.622 | **Nostalgia 0.884 ✅** |
| `textura de negativo Kodak, tira de contato` | Nostalgia | Solenidade 0.429 | **Nostalgia 0.854 ✅** |

Os 2 casos-alvo foram corrigidos com folga. Mas o Grupo A completo (30 casos) encontrou uma
regressão real:

| Caso (Grupo A) | Esperado | Antes | Depois (2 frases) |
|---|---|---|---|
| `headshot com fundo neutro de estúdio` | **Corporativo (Focado)** | Corporativo 0.547 (correto) | **Nostalgia 0.564 (errado)** |

Este caso é um dos 3 casos centrais de Corporativo — corrigido justamente na **rodada 1** desta
série. A regressão o devolveu ao estado de falha.

### Isolando o driver (breakdown por frase)

| Score | Frase | Âncora |
|---|---|---|
| **0.564** | `retrato com grão de filme genuíno e visível, tons quase em preto e branco, textura autêntica de negativo fotográfico revelado quimicamente` (nova) | Nostalgia |
| 0.547 | `pose formal e distante para estúdio, expressão neutra e contida, sem intimidade ou emoção pessoal` | Corporativo |
| 0.442 | `textura de negativo de filme Kodak, tira de contato...` (nova, a outra frase) | Nostalgia |

A frase nova 1 (`"retrato com grão de filme..."`) é a driver, por uma margem mínima (0.564 vs.
0.547). A palavra `"retrato"` e a descrição genérica de tons/textura fotográfica generalizaram
demais, colando com qualquer descrição de "foto de retrato bem composta", inclusive um headshot
corporativo. A frase 2 (`"textura de negativo de filme Kodak..."`) não é implicada (0.442, bem
abaixo) — vocabulário mais específico (Kodak, tira de contato, arranhões) não colide com Corporativo.

## Ação: isolar e reverter só a frase problemática

Conforme o padrão das rodadas 4/5, **não revertidas as 2 juntas.** Revertida só a frase 1
(`"retrato com grão de filme..."` → volta a `"película, polaroid, filme de 35mm"`, texto original).
Mantida a frase 2 (`"textura de negativo de filme Kodak..."`). Embeddings regenerados.
`data/raw/knowledge_anchors.json` permanece com **55 frases** (uma reescrita ficou, a outra reverteu
ao texto original — a contagem de frases de Nostalgia continua 6).

### Resultado final (após isolar)

| Caso-alvo | Esperado | Resultado final |
|---|---|---|
| `grão de filme genuíno em retrato quase preto e branco` | Nostalgia | **❌ Solenidade 0.622 — voltou a falhar** (a frase que resolvia era a mesma que causava a regressão) |
| `textura de negativo Kodak, tira de contato` | Nostalgia | **✅ Nostalgia 0.854 — mantido** |
| `headshot com fundo neutro de estúdio` (Grupo A, Corporativo) | Corporativo | **✅ Corporativo 0.547 — regressão desfeita** |

## Checagem de regressão completa (estado final)

- **Grupo A completo (30 casos):** **29/30 idênticos** — a única mudança é o próprio caso-alvo de
  Nostalgia que permanece corrigido (`"textura de negativo Kodak..."`). Zero divergência em qualquer
  outra âncora.
- **Casos de guarda (Solenidade ×4, Vitalidade ×3):** todos com score idêntico antes/depois. O único
  "alarme" (`"produto isolado em fundo branco"` → `__tecnico__` 0.511) é o mesmo falso-alarme
  pré-existente já documentado nas rodadas 3, 5 e 7 (score idêntico em ambos os lados, não
  relacionado a esta rodada).
- **Caso de observação** (`"estética vintage só que digitalmente perfeita, sem grão real"`): score
  idêntico (0.578) — nenhum efeito colateral, nem positivo nem negativo, como esperado (não era alvo
  desta rodada).
- **Checagem cruzada rodadas 1-7** (6 casos-alvo): todos com score idêntico, sem mudança.
- **Corpus técnico (9 casos):** 9/9 idênticos, `__tecnico__` intacto.

## Critério de parada — por frase

| Frase | Causou regressão? | Resolveu o alvo? | Decisão |
|---|---|---|---|
| `"retrato com grão de filme genuíno..."` | **Sim** (Corporativo → Nostalgia) | Sim (0.884) | **Revertida** |
| `"textura de negativo de filme Kodak..."` | Não | Sim (0.854) | **Mantida** |

**Critério geral: parcialmente atingido.** 1 de 2 casos-alvo permanece corrigido
(`"textura de negativo Kodak, tira de contato"`, que também era o caso mais grave do diagnóstico —
quase empate técnico com Vitalidade). O outro (`"grão de filme genuíno em retrato quase preto e
branco"`) volta a ser uma limitação conhecida. Zero regressão no estado final.

## Estado atual do repositório

**Aplicado, parcialmente.** `data/raw/knowledge_anchors.json` mantém 55 frases (Nostalgia continua
com 6 — a frase de "negativo Kodak" ficou reescrita, a de "retrato com grão de filme" voltou ao
texto original de lista de palavras). `src/scripts/anchors/sbert_json.py` reflete esse estado.

## Pendência / limitação conhecida atualizada

`"grão de filme genuíno em retrato quase preto e branco"` (esperado Nostalgia, cai em Solenidade
0.622) — fechado como limitação conhecida nesta rodada. A única frase testada capaz de resolvê-lo
generalizava demais em torno da palavra "retrato" e colidia com um caso central de Corporativo já
corrigido. Uma eventual rodada 9 poderia tentar uma variação sem a palavra "retrato" (ex.: focar
só em "grão"/"textura"/"preto e branco" sem enquadramento de "retrato"), mas isso não foi tentado
aqui — segue a mesma disciplina de não insistir numa 3ª variação na mesma rodada.

## Atualização da classificação de saúde

Nostalgia (Analógico) estava classificada 🔴 Defasada — pior classificação restante do sistema, com
1/3 de acerto no Grupo A. Com o caso mais grave do diagnóstico (`"textura de negativo Kodak, tira de
contato"`, antes um quase-empate técnico entre Solenidade e Vitalidade, ambos abaixo de 0.43) agora
resolvido com placar de 0.854, o acerto do Grupo A sobe de 1/3 para 2/3. A classificação sobe para
**🟠 Defasada** — ainda não saudável (1 caso central sem solução, a armadilha Grupo B "vintage
digitalmente perfeito" continua sem tratamento), mas deixa de ser a pior âncora do sistema.
