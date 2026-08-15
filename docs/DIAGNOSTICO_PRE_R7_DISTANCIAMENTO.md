# Diagnóstico pré-rodada 7 — Distanciamento (Low-key)

Só diagnóstico, nenhuma frase-âncora foi editada. Estado do repositório inalterado desde a rodada 6
(`REFINO_SIMPLICIDADE_R6.md`): 54 frases, Distanciamento nunca tocada em nenhuma rodada 1-6.

## 1. Frases atuais de Distanciamento (Low-key)

4 frases:
1. `foto escura, sombria e pesada`
2. `lugar vazio, abandonado, desolado, concreto`
3. `solitário, isolado, triste, frio, melancólico, silencioso, distante`
4. `sensação de solidão, ninguém por perto, ambiente opressivo, luz baixa e dura`

## 2. Grupo A — 3 casos centrais (top1 / score / gap)

| Caso | Top1 | Score | Top2 | Gap | Hit? |
|---|---|---|---|---|---|
| `poste de luz solitário contra escuridão quase total` | **Vitalidade (Ação)** | 0.725 | Distanciamento 0.697 | 0.028 | ❌ **MISS** |
| `corredor vazio e escuro` | Distanciamento (Low-key) | 0.614 | Solenidade 0.533 | 0.081 | ✅ |
| `silhueta isolada, ninguém por perto` | Distanciamento (Low-key) | 0.658 | Solenidade 0.572 | 0.086 | ✅ |

**Achado novo, não detalhado no diagnóstico original:** o miss do Grupo A é `"poste de luz
solitário contra escuridão quase total"` → vai pra **Vitalidade (Ação)**, não pra Solenidade ou
Sublime como as narrativas anteriores sugeririam. O relatório original só publicava os agregados
(score médio 0.666, 2/3 acerto) sem apontar qual caso falhava nem pra onde ia — esta é a
identificação exata. Gap de só 0.028 entre Vitalidade e a própria Distanciamento — praticamente um
empate, a âncora certa perde por pouco.

## 3. Grupo B — casos de fronteira envolvendo Distanciamento

| Caso | Esperado | Trap documentado | Top1 (atual) | Score | Gap | Resultado |
|---|---|---|---|---|---|---|
| `paisagem grandiosa mas fotografada no escuro` | **Distanciamento** | Sublime | Sublime | 0.842 | 0.120 | ❌ TRAP (confirma Distanciamento↔Sublime) |
| `pessoa sozinha ao entardecer, sombras longas` | `NAO_DISTANCIAMENTO` (ver nota) | Distanciamento | **Distanciamento** | 0.702 | 0.107 | ❌ TRAP |
| `montanha grandiosa fotografada à noite` | Sublime | Distanciamento (armadilha testada) | Sublime | 0.755 | 0.207 | ✅ HIT (a armadilha não se concretizou aqui) |
| `ambiente escuro mas festivo e animado` | Noturno | Distanciamento (armadilha testada) | Noturno | 0.705 | 0.050 | ✅ HIT (a armadilha não se concretizou aqui) |
| `show de rock em ambiente escuro` | Noturno | Vitalidade (armadilha documentada, não Distanciamento) | **Distanciamento** | 0.600 | 0.084 | ❌ OUTRA (Distanciamento venceu por acidente, sem estar em nenhuma das 2 opções documentadas) |

**Nota sobre `"pessoa sozinha ao entardecer, sombras longas"`:** o rótulo `NAO_DISTANCIAMENTO
(horario_errado)` no corpus do diagnóstico original **não** aponta uma âncora esperada alternativa —
é um caso construído especificamente pra confirmar que o sistema **não deveria** escolher
Distanciamento aqui (entardecer/sombras longas é um horário/qualidade de luz diferente da "escuridão
opressiva" que a âncora pretende capturar; não há uma âncora "certa" definida no corpus para este
caso, só a regra negativa). Resultado atual: Distanciamento venceu (0.702) — a armadilha se
confirma, o sistema continua sem essa distinção.

**Resumo:** dos 5 casos de fronteira que envolvem Distanciamento (como esperada, como armadilha
documentada, ou como vencedora acidental), **2 caem na armadilha, 2 escapam dela (a âncora oposta
vence por conta própria, não porque Distanciamento tenha ficado mais precisa), e 1 é um caso
"errante"** onde Distanciamento vence um caso que nem era pra ela nem pra a armadilha documentada.
Isso é consistente com a leitura do usuário de "gap médio baixo sugere confusão frequente com
vizinhas": Distanciamento está em disputa apertada em praticamente todas as direções — perde para
Vitalidade no seu próprio Grupo A, perde para Sublime quando a cena é grandiosa, e vence por engano
quando não devia (entardecer, show de rock).

## 4. Breakdown por frase individual — os 2 casos de maior erro

### Caso A (Grupo A, miss não documentado antes): `"poste de luz solitário contra escuridão quase total"`

| Score | Frase | Âncora |
|---|---|---|
| **0.725** | `foto clara, branca, superexposta, lavada de luz, high key, muito brilho, estourou de branco, claridade extrema, tudo iluminado, sem sombra` | Vitalidade |
| 0.697 | `foto escura, sombria e pesada` | Distanciamento |
| 0.613 | `sensação de solidão, ninguém por perto, ambiente opressivo, luz baixa e dura` | Distanciamento |
| 0.596 | `cores vibrantes, saturadas, cena com energia e movimento` | Vitalidade |
| 0.376 | `solitário, isolado, triste, frio, melancólico, silencioso, distante` | Distanciamento |
| 0.374 | `lugar vazio, abandonado, desolado, concreto` | Distanciamento |

**Achado crítico:** a frase vencedora é `"foto clara, branca, superexposta... sem sombra"` — que
descreve o **oposto exato** da cena de teste (escuridão quase total). É o mesmo padrão de
antônimo/negação que não funciona em embeddings de mean pooling, já documentado nas rodadas 2, 3 e
5 — mas desta vez entre **duas âncoras diferentes** (Vitalidade × Distanciamento), não dentro do
mesmo par já mapeado. A palavra "luz" aparece nos dois lados (`"poste de luz"` no teste,
"lavada de luz"/"claridade" na frase de Vitalidade) e pesa a favor da similaridade independente do
sentido oposto (uma luz isolada na escuridão vs. uma cena inteira estourada de brilho).

### Caso B (Grupo B, armadilha documentada): `"paisagem grandiosa mas fotografada no escuro"`

| Score | Frase | Âncora |
|---|---|---|
| **0.842** | `foto de paisagem enorme e impressionante` | Sublime |
| 0.722 | `foto escura, sombria e pesada` | Distanciamento |
| 0.635 | `pessoa pequena perto da natureza, horizonte infinito, pôr do sol dramático, deslumbrante` | Sublime |
| 0.598 | `natureza selvagem, montanha, oceano, céu` | Sublime |
| 0.460 | `épico, grandioso, majestoso, tirar o fôlego, imensurável, contemplativo` | Sublime |
| 0.411 | `sensação de solidão, ninguém por perto, ambiente opressivo, luz baixa e dura` | Distanciamento |
| 0.386 | `lugar vazio, abandonado, desolado, concreto` | Distanciamento |
| 0.305 | `solitário, isolado, triste, frio, melancólico, silencioso, distante` | Distanciamento |

**Achado:** nenhuma das 4 frases de Distanciamento menciona escala/paisagem/natureza — Sublime vence
com folga (0.842 vs. 0.722) porque "paisagem grandiosa" mapeia direto pra `"foto de paisagem enorme
e impressionante"`, e a melhor frase de Distanciamento só cobre o eixo "escuro", não o eixo
"grandioso mas escuro" combinado. Confirma exatamente a hipótese já registrada no diagnóstico
original (`"confunde com Sublime quando o texto tem paisagem + escuridão"`).

## 5. Frases-lista de palavras soltas em Distanciamento

Sim — o mesmo padrão já corrigido em `__tecnico__` (rodada 1) e Simplicidade (rodada 6) está
presente aqui, e de forma ainda mais concentrada:

| Frase | Classificação |
|---|---|
| `foto escura, sombria e pesada` | Lista curta de adjetivos, sem sujeito/cena — mais perto de lista do que de prosa |
| `lugar vazio, abandonado, desolado, concreto` | **Lista pura de adjetivos**, sem estrutura de frase |
| `solitário, isolado, triste, frio, melancólico, silencioso, distante` | **Lista pura de adjetivos** (7 termos soltos), sem estrutura de frase |
| `sensação de solidão, ninguém por perto, ambiente opressivo, luz baixa e dura` | Semi-prosa (tem "sensação de", "ninguém por perto" como fragmento de cláusula), mas ainda é uma sequência de fragmentos separados por vírgula, não uma frase única com sujeito e cenário coerente |

**Nenhuma das 4 frases descreve uma cena/situação em prosa natural completa** (sujeito + verbo +
contexto), ao contrário do padrão que funcionou nas correções anteriores (ex.: `"pessoa agindo de
forma natural e casual, sem pose para a câmera, autêntica no ambiente familiar do cotidiano"`, de
Simplicidade r6). Isso é consistente com os 2 achados dos passos 2-4: a âncora tem vocabulário
disperso em adjetivos soltos e nenhuma frase cobre cenários combinados (ex.: "grandioso mas escuro",
"luz isolada numa escuridão", "horário de sombras longas mas não opressivo") — exatamente o tipo de
nuance que só aparece quando a frase descreve uma situação específica, não uma lista de traços.

## Estado do repositório

Inalterado — nenhuma frase-âncora foi editada, nenhum embedding foi regenerado nesta tarefa.
