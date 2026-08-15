# Diagnóstico de Saúde das Âncoras Semânticas — Photus B

Nenhum arquivo de âncoras/thresholds foi alterado. Script reaproveitável em
`scripts/anchors/diagnose_router_health.py`; resultados brutos em
`data/processed/router_health_diag_results.json`.

---

## Passo 1 — Mapeamento do Photus B

### 1.0 Achado crítico: existem DOIS "roteadores" no repo, só um está vivo

- `src/domain/application/strategies/embedding/semantic_router.py` (`SemanticRouter`)
  — **código morto/quebrado**. `__init__` faz `self._anchors_ids = List[str] = []`
  (encadeamento de atribuição inválido: tenta fazer `List[str] = []`, o que
  lança `TypeError` em runtime). `load_from_json` lê o JSON mas **descarta o
  resultado** — o código que popularia `_anchors_ids/_phrases/_embeddings`
  está comentado. `get_top_k` assume `self._embeddings` como array numpy que
  nunca é preenchido. Essa classe não é importada por nenhuma rota da API nem
  pelo CLI — só aparece em entidades/pipeline (`route_result.py`,
  `classification.py`, `semantic_routing.py`) que também não estão
  conectados a nada em produção.
- `src/domain/application/use_cases/categorize_text.py` (`CategorizationService`)
  — **este é o roteador real**, usado por `POST /categorize`
  (`src/presentation/api/v1/routes/classification.py`) e pelo CLI
  `scripts/anchors/run_custom_sentences.py`. É essa a implementação
  reaproveitada na bateria de testes abaixo (`route_technical_to_mistral=False`
  para não gastar chamadas reais ao Mistral).

**Recomendação imediata (fora do escopo de "não alterar âncoras/thresholds",
é sobre higiene de código):** decidir se `SemanticRouter`/`semantic_routing.py`
serão terminados ou removidos — hoje é confuso ter dois roteadores, um deles
quebrado, coexistindo no domínio.

### 1.1 Lógica de roteamento real (`CategorizationService.categorize`)

1. Gera embedding do texto via `SentenceTransformerAdapter`
   (`paraphrase-multilingual-MiniLM-L12-v2`, 384 dims).
2. `rank_anchors`: calcula cosseno contra **todas as 49 frases individuais**
   das 11 âncoras (10 semânticas + `__tecnico__`), depois deduplica por
   `anchor_id` mantendo o melhor score por âncora (não é média por âncora —
   é o **máximo**).
3. `_is_technical`: `technical=True` se (a) regex `f/\d`, `iso\s?\d`, `\d+/\d+s`
   casar no texto (bypassa threshold), OU (b) score do `__tecnico__` no
   ranking ≥ `THRESHOLD_TECNICO`.
4. Se técnico e `route_technical_to_mistral=True`, chama Mistral com o
   prompt `technical.md`. Caso contrário, retorna a âncora top-1.
5. `low_confidence=True` se `score_top1 < CONFIDENCE_THRESHOLD_LOW` — **isso
   só marca uma flag**, não re-roteia para nenhum fallback; a âncora top-1
   ainda é retornada como resposta.

### 1.2 Frases-âncora atuais (conteúdo literal usado para embedding)

| Âncora | Frases (verbatim) |
|---|---|
| **Vitalidade (Ação)** (5) | "foto de esporte com ação e movimento físico intenso" · "corrida, salto, esforço" · "atlético, dinâmico, adrenalina, suor, força, intenso" · "foto clara, branca, superexposta, lavada de luz, high key, muito brilho, estourou de branco, claridade extrema, tudo iluminado, sem sombra" · "cores vibrantes, saturadas, cena com energia e movimento" |
| **Solenidade (Estase)** (4) | "foto parada e silenciosa" · "ambiente organizado, limpo e simétrico" · "calmo, sereno, tranquilo, neutro, minimalista, equilibrado, suave" · "sem bagunça, sem movimento, tudo no lugar, paz visual, elegante e contido" |
| **Conexão (Close-up)** (3) | "foto de rosto humano em plano fechado, close extremo, sorriso, olhar direto, expressão emocional" · "feliz, alegre, acolhedor, caloroso, amigável, empático, íntimo, carinhoso" · "aproximação, afeto, presença humana, emoção no rosto, calor humano" |
| **Distanciamento (Low-key)** (4) | "foto escura, sombria e pesada" · "lugar vazio, abandonado, desolado, concreto" · "solitário, isolado, triste, frio, melancólico, silencioso, distante" · "sensação de solidão, ninguém por perto, ambiente opressivo, luz baixa e dura" |
| **Simplicidade (Cotidiano)** (4) | "foto comum do dia a dia, sem produção" · "casa, cozinha, rua, trabalho, rotina" · "natural, simples, casual, autêntico, doméstico, familiar, sem pose" · "luz de janela, cena ordinária, momento espontâneo, vida real sem filtro" |
| **Conflito (Caos)** (4) | "foto de confusão e desordem urbana, rua suja e multidão agitada" · "cena caótica, tensão" · "bagunçado, áspero, agressivo, estressante, poluído, urbano e hostil" · "sensação de conflito, ambiente carregado, cena pesada, perturbador visualmente" |
| **Nostalgia (Analógico)** (6) | "fotografia com cara de antiga, velha, de outro tempo" · "película, polaroid, filme de 35mm" · "cores desbotadas, granulado, retrô, vintage, anos 70, anos 80, anos 90, anos 2000" · "saudade, memória, passado, afeto antigo, estética analógica, revelado à mão" · "subcultura, emo, punk, gótico, alternativo, indie, rock, banda, show underground" · "sensação de nostalgia, saudade, atmosfera de outro tempo, memória afetiva do passado" |
| **Sublime (Paisagem)** (4) | "foto de paisagem enorme e impressionante" · "natureza selvagem, montanha, oceano, céu" · "épico, grandioso, majestoso, tirar o fôlego, imensurável, contemplativo" · "pessoa pequena perto da natureza, horizonte infinito, pôr do sol dramático, deslumbrante" |
| **Corporativo (Focado)** (3) | "foto profissional para currículo, linkedin ou apresentação de trabalho" · "sério, confiável, formal, neutro, limpo, estúdio, fundo liso" · "imagem de executivo, chefe, funcionário, empresário, headshot, foto de perfil profissional" |
| **Noturno (Festa)** (3) | "foto de festa, balada, celebração, evento social à noite" · "amigos juntos, dança, euforia, animado, desinibido, multidão feliz" · "encontro, bebida, show, rave, clube, farra, agito, turma reunida, comemoração" |
| **`__tecnico__`** (9) | Listas de jargão técnico puro (abertura/f-stop/bokeh; exposição/histograma; shutter speed; ISO/ruído; iluminação de estúdio; temperatura de cor/kelvin; raw/edição; composição/proporção; e **uma** frase em linguagem semi-natural: "deixa o fundo borrado, fundo sumiu... expor para as sombras... forçar o ISO...") |

Total: **49 frases / 11 âncoras** (`metadata.total_anchors=49`,
modelo `paraphrase-multilingual-MiniLM-L12-v2`, dim 384).

### 1.3 Thresholds atuais

| Nome no código | Valor | Papel |
|---|---|---|
| `THRESHOLD_TECNICO` | **0.48** | score mínimo do `__tecnico__` no ranking para classificar como técnico (bypassado por regex) |
| `CONFIDENCE_THRESHOLD_LOW` | **0.45** | abaixo disso, `low_confidence=True` (é o equivalente ao `THRESHOLD_SCORE` pedido — não há constante com esse nome exato) |
| `THRESHOLD_GAP` | **não existe** | não há nenhuma lógica de gap top1/top2 no roteador em produção — o script legado `evaluate_anchors.py` e o `SemanticRouter` morto também não implementam gap |

**Achado:** o prompt original assume rota `fast_track / fallback / tecnico`
baseada em score+gap. Isso **não existe hoje**: a única bifurcação real é
`technical` (regex OU score `__tecnico__`) vs. não-técnico, e dentro de
não-técnico só existe a flag informativa `low_confidence`, sem qualquer
re-roteamento. Gap entre 1º/2º lugar é calculado abaixo só para fins de
diagnóstico (não é usado pelo sistema hoje).

---

## Passo 2 e 3 — Corpus e bateria

Corpus com 51 casos (Grupo A=30, B=16, C=5), rodado via
`CategorizationService.categorize(text, top_k=3, route_technical_to_mistral=False)`
reaproveitando o roteador real. Script: `scripts/anchors/diagnose_router_health.py`.
Resultados brutos: `photus_b_diag_results.json`.

---

## Passo 4 — Relatório de saúde por âncora (Grupo A — casos centrais)

| Âncora | score médio | gap médio | acerto top-1 | caiu em low_confidence |
|---|---|---|---|---|
| Vitalidade (Ação) | 0.575 | 0.083 | 3/3 | 0/3 |
| Solenidade (Estase) | 0.618 | 0.054 | 2/3 | 1/3 |
| Conexão (Close-up) | 0.666 | 0.141 | 2/3 | 0/3 |
| Distanciamento (Low-key) | 0.666 | 0.065 | 2/3 | 1/3 |
| Simplicidade (Cotidiano) | 0.468 | 0.037 | 2/3 | **2/3** |
| Conflito (Caos) | 0.615 | 0.123 | 2/3 | 0/3 |
| Nostalgia (Analógico) | 0.600 | 0.119 | 1/3 | 1/3 |
| Sublime (Paisagem) | **0.701** | **0.280** | 3/3 | 0/3 |
| Corporativo (Focado) | 0.534 | 0.039 | 1/3 | **2/3** |
| Noturno (Festa) | 0.594 | 0.094 | 3/3 | 0/3 |

Leitura:
- **Sublime (Paisagem)** é de longe a âncora mais saudável — score e gap
  altos, 3/3 corretas. Vocabulário ("épico", "grandioso", "pessoa pequena
  perto da natureza") é distintivo e pouco ambíguo.
- **Simplicidade (Cotidiano)** e **Corporativo (Focado)** são as mais frágeis
  mesmo em casos que deveriam ser óbvios: 2/3 e 2/3 dos casos centrais caem
  abaixo de `CONFIDENCE_THRESHOLD_LOW=0.45`. As frases de ambas são muito
  genéricas ("natural, simples, casual..." / "sério, confiável, formal...")
  — vocabulário de vibe central, sem nada que as separe de vizinhas
  (Solenidade, Conexão).
- **Nostalgia (Analógico)** erra 2/3 dos casos centrais apesar de ter 6
  frases (a âncora com mais frases) — sinal de que quantidade de frases não
  compensa falta de foco semântico; possivelmente as frases de subcultura
  ("emo, punk, gótico...") estão puxando o centroide para um sentido
  diferente do testado ("grão de filme", "negativo Kodak").

---

## Passo 4 (cont.) — Grupo B (fronteira) e Grupo C (técnico)

**Grupo B: 5/16 (31%) acertaram a âncora esperada, 9/16 (56%) caíram na
armadilha documentada, 2/16 (13%) foram para uma terceira âncora.** Nenhum
caso de fronteira foi absorvido por um "fallback por ambiguidade" — porque,
como visto no Passo 1.3, esse mecanismo não existe; o sistema sempre entrega
uma âncora top-1 com confiança aparente, mesmo quando ela é a armadilha.

**Grupo C: apenas 1/5 (20%) dos casos técnicos foram roteados como
`technical=True`**, e esse único acerto foi via **regex** (`f/1.8`), não via
score semântico do `__tecnico__`. As 4 frases técnicas em linguagem natural
("deixa o fundo borrado e o rosto nítido", "profundidade de campo rasa",
"subexposição intencional em low-key", "estoure o brilho dos realces") todas
ficaram abaixo de 0.48 no score `__tecnico__` (0.446, 0.459, 0.402, 0.432 —
todas próximas mas abaixo do threshold) e duas delas (`profundidade de campo
rasa` → Sublime 0.493; `estoure o brilho dos realces` → Simplicidade 0.672)
foram roteadas com confiança alta para âncoras semânticas completamente
erradas, sem nenhum sinal de que eram, na verdade, jargão técnico.

Isso é o achado mais grave do diagnóstico: **a detecção de `__tecnico__` por
embedding está sistematicamente abaixo do threshold para frases técnicas
formuladas em prosa**, porque as 9 frases-âncora de `__tecnico__` são quase
todas listas de palavras-chave soltas ("abertura, diafragma, f-stop..."),
não frases em linguagem natural — o embedding delas fica distante de frases
como "deixa o fundo borrado", mesmo essas sendo semanticamente técnicas. A
única frase da âncora escrita como prosa ("deixa o fundo borrado, fundo
sumiu, fundo sumir...") já cobre exatamente esse padrão, mas 1 frase entre 9
não tem peso suficiente no score agregado.

---

## Passo 5 — Matriz de confusão (Grupo B: esperado → obtido)

| Esperado ↓ / Obtido → | Contagem |
|---|---|
| Noturno (Festa) → Noturno (Festa) | 2 |
| Noturno (Festa) → **Distanciamento (Low-key)** | 1 |
| Conflito (Caos) → **Vitalidade (Ação)** | 1 |
| Conflito (Caos) → **Conexão (Close-up)** | 1 |
| Conexão (Close-up) → Conexão (Close-up) | 1 |
| Conexão (Close-up) → **Corporativo (Focado)** | 1 |
| Sublime (Paisagem) → Sublime (Paisagem) | 2 |
| Solenidade (Estase) → **Simplicidade (Cotidiano)** | 1 |
| Vitalidade (Ação) → **Noturno (Festa)** | 1 |
| Distanciamento (Low-key) → **Sublime (Paisagem)** | 1 |
| Simplicidade (Cotidiano) → **Corporativo (Focado)** | 1 |
| Corporativo (Focado) → **Noturno (Festa)** | 1 |
| (ambíguo/descarte) → Nostalgia (Analógico) | 1 |
| (não deveria ser Distanciamento) → **Distanciamento (Low-key)** | 1 |

**Pares de menor separabilidade textual identificados** (cada um apareceu
como armadilha vencedora pelo menos uma vez):

- **Corporativo (Focado) ↔ Conexão (Close-up) ↔ Simplicidade (Cotidiano)** —
  triângulo de confusão: "retrato de estúdio emotivo" perde para
  Corporativo; "roupa profissional em ambiente real" também vira
  Corporativo; "coquetel corporativo" vira Noturno. Corporativo está "sugando"
  casos de outras três âncoras.
- **Distanciamento (Low-key) ↔ Sublime (Paisagem)** — confusão nos dois
  sentidos (paisagem escura vira Sublime; o inverso também aconteceu no
  Grupo A informalmente). Ambas competem por "grandiosidade" e "escuridão"
  sem que a âncora capture bem a combinação dos dois eixos.
- **Conflito (Caos) ↔ Vitalidade (Ação) / Conexão (Close-up)** — "multidão"
  e "rosto" nas frases de Conflito são fracos; multidão pura puxa para
  Conexão (rosto) e dor/esforço físico puxa para Vitalidade.
- **Noturno (Festa) ↔ Distanciamento (Low-key) / Corporativo (Focado)** —
  a palavra "escuro" sozinha (sem "festivo") puxa para Distanciamento; "cena
  social formal" puxa Noturno mesmo sem festa.

Isso corresponde ao que a documentação de calibração do Photus A já havia
identificado como pares vizinhos problemáticos — a confirmação aqui é que o
**texto das âncoras do Photus B não herdou esse conhecimento fino de
fronteira**: nenhuma frase menciona explicitamente os contrastes ("grandioso
mas fotografado no escuro NÃO é Sublime", "multidão sem tensão NÃO é
Conflito").

---

## Passo 6 — Recomendações (diagnóstico apenas, nada foi implementado)

### Classificação de saúde por âncora

| Âncora | Status | Motivo |
|---|---|---|
| Sublime (Paisagem) | ✅ Saudável | score/gap altos, 3/3 central, 2/2 fronteira relevante |
| Vitalidade (Ação) | 🟡 Saudável com ressalva | forte no central, mas perde 2 casos de fronteira (Conflito, multidão-sem-tensão) |
| Noturno (Festa) | 🟡 Saudável com ressalva | forte no central, mas confunde com Distanciamento/Corporativo em fronteira |
| Conexão (Close-up) | 🟡 Defasada parcial | boa no central, mas perde para Corporativo em contexto de estúdio |
| Conflito (Caos) | 🟠 Defasada | perde 2/2 casos de fronteira testados; vocabulário de "multidão" e "rosto" é fraco |
| Solenidade (Estase) | 🟠 Defasada | 1/3 fallback no central; perde para Simplicidade quando a cena é "produzida" |
| Distanciamento (Low-key) | 🟠 Defasada | confunde com Sublime quando o texto tem paisagem + escuridão |
| Nostalgia (Analógico) | 🔴 Defasada | pior taxa de acerto no central (1/3); frases de subcultura parecem desviar o centroide |
| Corporativo (Focado) | 🔴 Defasada | pior desempenho geral: 1/3 central + "rouba" 3 casos de fronteira de outras âncoras |
| Simplicidade (Cotidiano) | 🔴 Defasada | maior taxa de fallback no central (2/3); vocabulário genérico demais |
| `__tecnico__` | 🔴 Muito defasada | só 20% de detecção correta em jargão formulado como prosa; depende quase 100% do regex |

### Sugestões concretas de frases a adicionar (priorizadas pelos pares de confusão do Passo 5)

- **Corporativo (Focado)**: adicionar frase que ancore "estúdio + neutro" SEM
  emoção/proximidade, contrastando explicitamente com Conexão — ex.: "pose
  formal e distante, sem expressão emocional, luz de estúdio técnica,
  ambiente profissional mesmo fora de um escritório".
- **Conexão (Close-up)**: adicionar contraste explícito com Corporativo —
  ex.: "retrato de estúdio mas com emoção genuína no rosto, olhar vivo, não
  é foto de currículo".
- **Distanciamento (Low-key)**: adicionar frase combinando paisagem +
  escuridão sem grandiosidade épica — ex.: "silhueta contra paisagem escura
  e vazia, sem drama, só solidão", para se separar de Sublime quando a
  imagem é grande mas noturna sem "épico".
- **Sublime (Paisagem)**: adicionar frase reforçando que grandiosidade
  vence mesmo de noite/passado — ex.: "paisagem grandiosa histórica ou
  noturna, a escala importa mais que a luz".
- **Conflito (Caos)**: adicionar frase sobre "multidão com tensão" separada
  de "multidão festiva" — ex.: "multidão apertada e hostil, rostos
  indistintos e ansiosos, sensação de sufocamento, não é celebração".
- **Simplicidade (Cotidiano)**: adicionar contraste explícito com Solenidade
  — ex.: "cena do dia a dia mas claramente encenada e estilizada não conta,
  isso é outra coisa" (ou frase equivalente reforçando "sem produção" com
  exemplos negativos).
- **`__tecnico__`**: converter a lista de palavras-chave em mais frases de
  prosa natural (a categoria tem 8 das 9 frases como listas de termos, só 1
  como prosa) — ex. adicionar 3–4 frases como "explica como deixar o fundo
  desfocado e o assunto nítido", "quero saber o ajuste de exposição para
  não estourar as luzes", "como configurar o ISO para reduzir ruído".
  Isso deve ser tratado com prioridade alta — é o pior resultado do
  diagnóstico.

### Thresholds

- `THRESHOLD_TECNICO=0.48` parece **alto demais** para captar jargão em
  prosa — 4 dos 5 casos técnicos ficaram entre 0.40–0.46, logo abaixo do
  threshold. Antes de reescrever as frases de `__tecnico__`, vale considerar
  baixar para ~0.42–0.44 como paliativo, mas o problema real é de
  vocabulário (poucas frases em prosa), não só de calibração numérica.
- `CONFIDENCE_THRESHOLD_LOW=0.45` parece razoável como sinalizador, mas hoje
  **não tem efeito prático** (só seta uma flag). Vale decidir se ele deveria
  de fato desviar para o Mistral (como o prompt original presumia com
  "fallback"), porque hoje casos de fronteira mal roteados (ex.: "cena
  social mas estática e formal, tipo coquetel corporativo" → Noturno,
  score 0.527, bem acima do threshold) **nem seriam sinalizados** como
  incertos.
- Não existe `THRESHOLD_GAP` — se a intenção é usar gap top1/top2 para
  decidir ambiguidade, essa lógica precisa ser criada do zero. Os dados do
  Grupo B mostram gaps baixos (0.017–0.15) tanto em acertos quanto em erros,
  então um threshold de gap sozinho não teria discriminado bem esses casos
  — score absoluto por âncora parece mais informativo que gap relativo aqui.

---

## Arquivos gerados

- `scripts/anchors/diagnose_router_health.py` — script standalone da bateria (reaproveita `CategorizationService`)
- `data/processed/router_health_diag_results.json` — 51 resultados brutos (score, gap, rota, hit/trap por caso)
- `docs/DIAGNOSTICO_SAUDE_ANCORAS.md` — este relatório
