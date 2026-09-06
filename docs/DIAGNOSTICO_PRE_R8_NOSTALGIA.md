# Diagnóstico pré-rodada 8 — Nostalgia (Analógico)

Só diagnóstico, nenhuma frase-âncora foi editada. Estado do repositório inalterado desde a rodada 7
(`REFINO_DISTANCIAMENTO_R7.md`): 55 frases, Nostalgia nunca tocada em nenhuma rodada 1-7.

## 1. Frases atuais de Nostalgia (Analógico)

6 frases (a âncora com mais frases do sistema):
1. `fotografia com cara de antiga, velha, de outro tempo`
2. `película, polaroid, filme de 35mm`
3. `cores desbotadas, granulado, retrô, vintage, anos 70, anos 80, anos 90, anos 2000`
4. `saudade, memória, passado, afeto antigo, estética analógica, revelado à mão`
5. `subcultura, emo, punk, gótico, alternativo, indie, rock, banda, show underground`
6. `sensação de nostalgia, saudade, atmosfera de outro tempo, memória afetiva do passado`

## 2. Grupo A — 3 casos centrais (top1 / score / gap)

| Caso | Top1 | Score | Top2 | Gap | Hit? |
|---|---|---|---|---|---|
| `grão de filme genuíno em retrato quase preto e branco` | **Solenidade (Estase)** | 0.622 | Vitalidade 0.552 | 0.069 | ❌ MISS |
| `textura de negativo Kodak, tira de contato` | **Solenidade (Estase)** | 0.429 | Vitalidade 0.412 | 0.016 | ❌ MISS (`low_confidence=True`) |
| `estética vintage de décadas passadas` | Nostalgia (Analógico) | 0.720 | Noturno 0.451 | 0.270 | ✅ HIT |

**1/3 acerto confirmado**, igual ao diagnóstico original. Os 2 misses agora convergem pro **mesmo
destino errado (Solenidade)** — achado consistente com o que a rodada 7 já tinha notado de relance
pro primeiro caso, mas nunca investigado.

O segundo caso (`"textura de negativo Kodak, tira de contato"`) é o mais grave dos dois: nenhuma
âncora, nem a própria Nostalgia, passa de 0.429 — é essencialmente um vazio semântico no sistema
(gap de só 0.016 entre Solenidade e Vitalidade, um empate técnico), com `low_confidence=True`.

## 3. Grupo B — casos de fronteira envolvendo Nostalgia

| Caso | Esperado | Trap documentado | Top1 (atual) | Score | Gap | Resultado |
|---|---|---|---|---|---|---|
| `estética vintage só que digitalmente perfeita, sem grão real` | AMBIGUO/DESCARTE | Nostalgia | **Nostalgia** | 0.578 | 0.078 | ❌ TRAP (confirmado) |
| `cena antiga mas grandiosa, tipo paisagem histórica` | Sublime | Nostalgia | Sublime | 0.732 | 0.091 | ✅ HIT (a armadilha não se concretizou) |

O primeiro caso confirma a armadilha documentada: o sistema deveria tratar "vintage digitalmente
perfeito, sem grão real" como ambíguo/descarte (não é uma foto analógica genuína), mas continua
roteando com confiança pra Nostalgia.

## 4. Breakdown por frase individual — os 2 casos de maior erro

### Caso A (Grupo A, maior miss confiante): `"grão de filme genuíno em retrato quase preto e branco"`

| Score | Frase | Âncora |
|---|---|---|
| **0.622** | `cena claramente produzida e estilizada, composição encenada com intenção estética evidente, resultado de produção fotográfica cuidadosa e deliberada` | Solenidade |
| 0.570 | `foto parada e silenciosa` | Solenidade |
| 0.450 | `fotografia com cara de antiga, velha, de outro tempo` | Nostalgia |
| 0.404 | `película, polaroid, filme de 35mm` | Nostalgia |
| 0.371 | `cores desbotadas, granulado, retrô, vintage, anos 70, anos 80, anos 90, anos 2000` | Nostalgia |

**Achado não previsto:** a frase vencedora é a que foi **adicionada na rodada 5** pra resolver a
confusão Solenidade↔Simplicidade (`"cena claramente produzida e estilizada..."`). Ela não foi
testada contra Nostalgia na época (Nostalgia não estava no escopo da rodada 5) e acabou generalizando
demais: "retrato... com intenção estética evidente" combina com qualquer descrição que soe como
"foto bem composta/deliberada", inclusive uma foto analógica genuína. É um efeito colateral
retroativo de uma rodada anterior, só descoberto agora que Nostalgia está sendo diagnosticada.
Mesmo a melhor frase de Nostalgia (`"fotografia com cara de antiga, velha, de outro tempo"`, 0.450)
fica bem abaixo — inclusive a frase que menciona literalmente "filme" (`"película, polaroid, filme
de 35mm"`) só chega a 0.404, mais fraca que o esperado dado que a palavra-chave está lá; sinal de
diluição por mean pooling (a frase tem só 3 termos, mas nenhum deles by itself é forte o bastante).

### Caso B (Grupo B, armadilha confirmada): `"estética vintage só que digitalmente perfeita, sem grão real"`

| Score | Frase | Âncora |
|---|---|---|
| **0.578** | `cores desbotadas, granulado, retrô, vintage, anos 70, anos 80, anos 90, anos 2000` | Nostalgia |
| 0.511 | `fotografia com cara de antiga, velha, de outro tempo` | Nostalgia |
| 0.500 | `foto clara, branca, superexposta, lavada de luz, high key, muito brilho...` | Vitalidade |
| 0.490 | `saudade, memória, passado, afeto antigo, estética analógica, revelado à mão` | Nostalgia |

**Mesmo padrão de negação-não-funciona já documentado nas rodadas 2, 3, 5 e 7:** a frase vencedora
contém literalmente `"granulado"`, e o texto de teste diz explicitamente `"sem grão real"` — o
oposto semântico. A palavra-raiz (grão/granulado) pesa a favor da similaridade independente da
negação. "Vintage" e "retrô" no texto reforçam ainda mais essa colisão.

## 5. Frases-lista de palavras soltas em Nostalgia

Sim — e de forma mais concentrada que em qualquer âncora corrigida até agora. Das 6 frases, **4 são
listas puras de palavras**:

| Frase | Classificação |
|---|---|
| `fotografia com cara de antiga, velha, de outro tempo` | Semi-prosa curta (tem alguma estrutura de frase, mas sem cenário/verbo de ação) |
| `película, polaroid, filme de 35mm` | **Lista pura** (3 substantivos soltos) |
| `cores desbotadas, granulado, retrô, vintage, anos 70, anos 80, anos 90, anos 2000` | **Lista pura** (8 termos soltos, incluindo 4 décadas listadas) |
| `saudade, memória, passado, afeto antigo, estética analógica, revelado à mão` | **Lista pura** (6 termos soltos) |
| `subcultura, emo, punk, gótico, alternativo, indie, rock, banda, show underground` | **Lista pura** (9 termos soltos) — e semanticamente fora do eixo "textura fotográfica analógica" testado no Grupo A, como o diagnóstico original já suspeitava |
| `sensação de nostalgia, saudade, atmosfera de outro tempo, memória afetiva do passado` | Semi-prosa fragmentada (mesmo padrão de Distanciamento antes da r7: fragmentos separados por vírgula, não uma frase única com sujeito e cena) |

**Nenhuma das 6 frases descreve uma cena fotográfica específica em prosa completa** (o padrão que
funcionou em `__tecnico__`, Simplicidade e Distanciamento). Isso é consistente com os achados dos
passos 2-4: o vocabulário está disperso em termos soltos, nenhuma frase cobre explicitamente
"textura de grão/negativo/revelação química" como um cenário coerente, e a frase 5 (subcultura/
música) provavelmente dilui ainda mais o centroide da âncora — confirmando a suspeita já registrada
no diagnóstico original (`"possivelmente as frases de subcultura... estão puxando o centroide para
um sentido diferente do testado"`), agora com evidência concreta de que os 2 casos centrais mais
fotográficos (grão de filme, negativo Kodak) realmente não conseguem vencer nem Solenidade nem
Vitalidade.

## Estado do repositório

Inalterado — nenhuma frase-âncora foi editada, nenhum embedding foi regenerado nesta tarefa.
