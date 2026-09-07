# Comparação de provider no fallback semântico: Claude Haiku vs. Mistral vs. DeepSeek vs. Llama 3.1 8B

Mesmos 46 casos (Grupo A + B), mesmo `prompts/fallback.md` (com as regras de fronteira, ver
`COMPARACAO_PROMPT_FALLBACK_REGRAS_FRONTEIRA.md`), mesmos thresholds (`score_min=0.63`,
`gap_min=0.04`), mesmo `LLMConnector`/`categorize_text.py` — a única variável trocada entre as
rodadas foi `LLM_MODEL_CURRENT_NAME` no `.env`. Objetivo: isolar o efeito do modelo, já que o prompt
e o código são idênticos em todas.

- Mistral: `data/processed/fallback_live_validation.json` (`mistral/ministral-14b-latest`)
- DeepSeek: `data/processed/fallback_live_validation__deepseek-deepseek-v4-flash__20260906-193354.json`
- Claude Haiku: `data/processed/fallback_live_validation__anthropic-claude-haiku-4-5-20251001__20260906-195225.json`
- Llama 3.1 8B (via OpenRouter): `data/processed/fallback_live_validation__openrouter-meta-llama-llama-3-1-8b-instruct__20260906-213429.json`

## Resultado agregado

| | Acurácia | Casos corretos | Resgates dos 12 difíceis | Regressões nos 34 fáceis | Tempo total (20 chamadas reais) |
|---|---|---|---|---|---|
| SBERT-only (baseline) | 73.9% | 34/46 | — | — | — |
| **Claude Haiku 4.5** | **89.1%** | **41/46** | 7/12 | **0/34** | 48.3s |
| **Mistral** (`ministral-14b-latest`) | 87.0% | 40/46 | 7/12 | 1/34 | 48.3s |
| **DeepSeek** (`deepseek-v4-flash`) | 84.8% | 39/46 | 7/12 | 2/34 | 119.7s |
| **Llama 3.1 8B** (OpenRouter) | 82.6% | 38/46 | 6/12 | 2/34 | **24.4s** |

Mesmo número de disparos (20/46) em todas — esperado, o gatilho é score/gap do SBERT, que não muda
entre rodadas. Em latência, **Llama é o mais rápido de longe** (metade do tempo de Claude/Mistral, 5x
mais rápido que DeepSeek) — coerente com ser um modelo 8B, bem menor que os outros três. Em acurácia
a ordem é Claude > Mistral > DeepSeek > Llama, com Claude sendo o único a fechar **zero regressões**.

## Os casos resgatados — Llama é o único que não fecha o conjunto completo

| Caso | Esperado | Claude | Mistral | DeepSeek | Llama 3.1 8B |
|---|---|---|---|---|---|
| `sobrecarga sensorial, nada no lugar` | Conflito | ✅ | ✅ | ✅ | ✅ |
| `grão de filme genuíno em retrato quase preto e branco` | Nostalgia | ✅ | ✅ | ✅ | ✅ |
| `pessoa em roupa profissional mas em ambiente real, não estúdio` | Simplicidade | ✅ | ✅ | ✅ | ✅ |
| `multidão animada mas com clima positivo, sem tensão` | Vitalidade | ✅ | ✅ | ✅ | ✅ |
| `rosto pequeno e dividido em meio a uma multidão` | Conflito | ✅ | ✅ | ✅ | ✅ |
| `atleta com expressão de dor extrema no rosto` | Conflito | ✅ | ✅ | ✅ | ✅ |
| `pessoa lendo sem posar` | Simplicidade | ✅ | ✅ | ✅ | ❌ (ver nota) |

**Claude, Mistral e DeepSeek resgatam exatamente o mesmo conjunto de 7**, sem exceção — evidência
forte de que o ganho vem das regras de fronteira do prompt, não de uma capacidade específica de um
modelo. **Llama 3.1 8B falha em 1 dos 7**, e de um jeito específico: seu `reasoning` pra
`"pessoa lendo sem posar"` está **correto** — *"a cena descreve uma situação cotidiana e real, sem
pose ou produção deliberada, o que sugere que a âncora é Simplicidade"* — mas o campo `anchor` do
JSON não bateu com nenhuma âncora conhecida (`_resolve_anchor_label` não resolveu, caiu no SBERT
top1 = Distanciamento, errado). Ou seja: **o modelo raciocinou certo mas não conseguiu preencher o
schema JSON corretamente** — uma falha de instruction-following no formato estruturado, não de
compreensão da regra. É o tipo de risco que cresce com modelos menores/mais baratos: a lógica pode
estar certa e o resultado sair errado mesmo assim, porque o pipeline depende do campo `anchor` vir
exato.

Os 5 casos que nenhum dos quatro resolve são os mesmos, pela mesma razão em todos: 3 "confiante e
errado" (score/gap altos demais pra disparar o fallback, nunca chegam a chamar o LLM), a colisão
`produto isolado em fundo branco` → `__tecnico__` (nem entra na branch do fallback semântico), e
`estética vintage... sem grão real` — que em todos os quatro o modelo reconhece como ambíguo/imitação
no `reasoning` (Llama: *"é uma imitação de estilo vintage e não uma reprodução analógica genuína"*),
mas como não existe âncora chamada assim, cai no mesmo fallback gracioso pro SBERT top1 (`Nostalgia`,
que já estava lá antes de qualquer chamada) — o resultado final não muda independente do provider.

## Regressões — Claude é o único sem nenhuma

| Provider | Caso que regrediu | Esperado | `reasoning` |
|---|---|---|---|
| **Claude Haiku** | — nenhuma | — | — |
| Mistral | `olhos fechados, luz de contorno, mão tocando o queixo` | Conexão → Solenidade | "luz de contorno (...) indica uma produção fotográfica intencional e estática (...) o foco não é um close-up emocional genuíno" |
| DeepSeek | `iluminação de estúdio limpa, roupa formal` | Corporativo → Solenidade | "iluminação de estúdio limpa indica produção fotográfica deliberada e controlada (...) roupa formal reforça uma estética sóbria e estática" |
| DeepSeek | `show com multidão eufórica` | Noturno → Vitalidade | "multidão eufórica em um show, sem contexto explícito de festa ou celebração noturna (...) energia e ação em multidões animadas sem tensão" |
| Llama 3.1 8B | `olhos fechados, luz de contorno, mão tocando o queixo` | Conexão → Solenidade | "atmosfera de introspecção e quietude (...) ausência de expressão facial e a postura relaxada indicam uma sensação de calma e introspecção" |
| Llama 3.1 8B | `multidão densa vista de cima` | Conflito → Vitalidade | "sugere uma atmosfera de agitação e movimento, mas não há indícios de tensão ou dor física ou emocional intenso, o que exclui Conflito" |

**`"olhos fechados, luz de contorno, mão tocando o queixo"` agora regride em 2 dos 4 providers**
(Mistral e Llama), com os dois citando o mesmo sinal (produção/iluminação deliberada) pra justificar
Solenidade em vez de Conexão. Com mais um provider testado, esse deixa de parecer ruído de um modelo
específico e passa a parecer **genuinamente um caso onde a regra de fronteira de Solenidade compete
de verdade com a de Conexão** — metade dos modelos testados pesa o sinal errado. Os outros dois casos
de regressão (DeepSeek x2, Llama em multidão densa) seguem o padrão já visto: a regra nova mais
próxima "puxa" o caso por um sinal superficial, ignorando que a âncora original já cobria esse
contexto. **Claude Haiku continua sendo o único que não caiu em nenhuma dessas armadilhas.**

## Veredito

**Claude Haiku 4.5 continua o melhor resultado**: maior acurácia (89.1%), zero regressões, latência
igual ao Mistral. **Llama 3.1 8B é o mais rápido e mais barato** (modelo bem menor), mas paga o preço
em acurácia (82.6%, o pior dos quatro) e, mais importante, introduz um **modo de falha novo**: raciocínio
certo com saída estruturada errada — um risco real pra um pipeline que depende do `anchor` vir exato
no JSON. Se o volume de chamadas ou custo por chamada for uma restrição forte, Llama é uma opção
viável (~5x mais rápido que DeepSeek, gratuito/barato via OpenRouter) desde que se aceite ~5 pontos a
menos de acurácia e essa fragilidade extra de formato. Pra qualidade máxima sem essa fragilidade,
Claude Haiku continua a escolha mais segura; Mistral é a alternativa sólida já testada em produção.
DeepSeek não tem vantagem em nenhum eixo (nem acurácia, nem latência, nem regressões) que justifique
escolhê-lo sobre os outros três neste corpus.

## Estado

Nenhuma mudança de código foi necessária pra rodar com nenhum dos quatro providers além do que já
foi feito (`LLMConnector` resolve a API key certa a partir do prefixo do `LLM_MODEL_CURRENT_NAME` —
`mistral/`, `deepseek/`, `anthropic/`/`claude/`, `openrouter/`, entre outros já mapeados em
`litellm_adapter.py`). Trocar de provider é só mudar essa variável no `.env`. Resultados brutos das
quatro rodadas nos caminhos listados no topo deste documento.
