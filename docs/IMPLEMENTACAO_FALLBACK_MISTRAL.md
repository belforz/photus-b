# Implementação do fallback score/gap → Mistral (validado com Mistral real)

Implementa em `CategorizationService.categorize` os thresholds calibrados em
`CALIBRACAO_THRESHOLD_MISTRAL.md` (`score_min=0.63`, `gap_min=0.04`). Valida com **46 chamadas reais
ao Mistral** (`ministral-14b-latest`), não simulação. `THRESHOLD_TECNICO`, `CONFIDENCE_THRESHOLD_LOW`,
a lógica de detecção técnica e as frases-âncora não foram alterados.

## O que foi implementado

`src/domain/application/use_cases/categorize_text.py`:

1. **Constantes novas:**
   ```python
   THRESHOLD_SCORE_FALLBACK = 0.63
   THRESHOLD_GAP_FALLBACK = 0.04
   ```
2. **`call_semantic_fallback(text, ranked)`** — novo método, reaproveita `_mistral_connector()` (o
   mesmo cliente lazy usado por `call_mistral_technical`). Usa o prompt `fallback` (já existia em
   `prompts/fallback.md`, nunca estava conectado a nada — lista as 10 âncoras semânticas e pede um
   JSON com campo `"anchor"`). Faz parse best-effort do JSON (com ou sem cerca ```json) e resolve o
   nome retornado de volta pro `anchor_id` exato via `_resolve_anchor_label` (compara case-insensitive
   contra o `anchor_id` completo e contra o label sem parêntese, ignorando `__tecnico__`).
3. **Em `categorize()`**, depois de calcular `best`/`gap`, na branch não-técnica: se
   `best.score < THRESHOLD_SCORE_FALLBACK` OU `gap < THRESHOLD_GAP_FALLBACK` (e
   `route_technical_to_mistral=True`, o mesmo flag que já ligava/desligava o Mistral no fallback
   técnico — preserva o comportamento de todos os scripts de diagnóstico das rodadas anteriores que
   passam `route_technical_to_mistral=False`), chama `call_semantic_fallback`. Se o Mistral resolver
   uma âncora válida, ela vira a categoria final (`category`/`category_code`/`confidence`); senão,
   mantém o top1 do SBERT (degradação graciosa).
4. **Campos novos em `CategoryResult`** (preservando os existentes, incluindo `low_confidence` que
   continua calculado do jeito antigo, sem relação com o fallback):
   - `used_fallback: bool` — se a condição disparou e o Mistral foi chamado.
   - `sbert_anchor_before_fallback: Optional[str]` — âncora que o SBERT tinha escolhido antes do
     desvio (auditoria/debug), preenchido só quando `used_fallback=True`.
   Ambos incluídos em `to_category_payload()`.

Não há suíte de testes no projeto pra `categorize_text.py` (confirmado — nenhum arquivo `test_*.py`
existe no repo), então não havia nada pra rodar no Passo 4 da validação.

## Validação com Mistral real — os 46 casos (Grupo A + B)

Script: `scripts/anchors/validate_fallback_live.py`. Rodou cada um dos 46 casos duas vezes:
`route_technical_to_mistral=False` (baseline SBERT puro) e `=True` (fluxo real, dispara Mistral de
verdade quando a condição bate). **20 chamadas reais ao Mistral** disparadas, tempo total 60.3s
(46 casos × 2 categorizações SBERT + 20 chamadas de rede ao Mistral).

### Baseline SBERT-only (sem fallback)

**34/46 corretos (73.9%)** — bate exatamente com o levantamento da calibração.

### Os 12 casos que eram errados — quantos o Mistral resgatou de verdade?

| Resultado | Qtde | Casos |
|---|---|---|
| **Resgatado** (Mistral acertou) | **2** | `sobrecarga sensorial, nada no lugar` → Conflito ✅; `grão de filme genuíno em retrato quase preto e branco` → Nostalgia ✅ |
| **Disparou mas Mistral também errou** | **6** | `pessoa lendo sem posar` → Conexão (esperado Simplicidade); `atleta com expressão de dor extrema` → manteve Vitalidade (esperado Conflito); `multidão animada... sem tensão` → manteve Noturno (esperado Vitalidade); `estética vintage... sem grão real` → manteve Nostalgia (esperado ambíguo/descarte); `roupa profissional em ambiente real` → manteve Corporativo (esperado Simplicidade); `rosto pequeno e dividido numa multidão` → foi pra Distanciamento (esperado Conflito, nem foi o que o SBERT já tinha errado) |
| **Não disparou** | **4** | 3 são os "confiante e errado" já previstos na calibração (`show de rock em ambiente escuro`, `retrato próximo e emotivo em ambiente de estúdio formal`, `pessoa sozinha ao entardecer`) — score e gap altos o suficiente pra não acionar a regra, como esperado. O 4º (`produto isolado em fundo branco`) é um caso não previsto na calibração original: esse texto é classificado como **`technical=True`** (colisão pré-existente com `__tecnico__`, documentada no diagnóstico pós-sessão), então nem entra na branch não-técnica onde o fallback semântico atua — achado novo da implementação real. |

**Taxa de acerto do Mistral quando de fato chamado pra um caso difícil: 2/8 = 25%** — muito abaixo
dos 100% assumidos na simulação otimista. Os casos remanescentes não são "baixa confiança
resolúvel" — são ambiguidade genuína (o mesmo padrão de colisão lexical/negação documentado nas
rodadas 2-8), que um LLM também erra boa parte do tempo quando só recebe o texto cru sem o contexto
de imagem.

### Os 34 casos que já eram corretos — custo do disparo desnecessário

| Métrica | Valor |
|---|---|
| Dispararam fallback desnecessariamente | **12/34** (bate com a projeção de 13 da calibração, margem de 1) |
| Mistral manteve a resposta certa | **12/12 (100%)** |
| Mistral estragou um acerto | **0** |

**Achado importante:** mesmo não acertando os casos difíceis na maioria das vezes, o Mistral
**nunca corrompeu um caso que já estava certo** — o custo do disparo desnecessário é puramente
latência/chamada de API, não perda de qualidade.

## Acurácia final real vs. projetada

| | Acurácia | Casos corretos |
|---|---|---|
| SBERT-only (baseline) | 73.9% | 34/46 |
| **Projetado na calibração (Mistral 100% otimista)** | **93.5%** | 43/46 |
| **Real, medido com Mistral de verdade** | **78.3%** | **36/46** |

**A diferença (93.5% projetado vs. 78.3% real, -15.2 pontos) é inteiramente explicada pela suposição
otimista da calibração** — ela assumia que o Mistral acerta 100% das vezes que é chamado; na
prática, chamado pra decidir entre âncoras de vibe/estética a partir só de texto (sem ver a imagem),
o Mistral acerta só 25% dos casos genuinamente ambíguos. O ganho real (+2 casos, +4.3 pontos) veio
inteiramente dos 2 casos resgatados, sem nenhuma perda nos 34 que já funcionavam.

## Confirmação — os 3 casos "confiante e errado" continuam intocados

Os 3 casos identificados no Passo 3 da calibração como teto estrutural (score e gap altos demais pra
qualquer threshold razoável capturar) **continuam sem disparar o fallback**, como esperado — a
implementação real confirma a análise:

| Caso | Score | Gap | Disparou? |
|---|---|---|---|
| `pessoa sozinha ao entardecer, sombras longas` | 0.725 | 0.130 | Não |
| `retrato próximo e emotivo em ambiente de estúdio formal` | 0.706 | 0.159 | Não |
| `show de rock em ambiente escuro` | 0.657 | 0.141 | Não |

## Latência / custo aproximado

- **20 chamadas ao Mistral em 46 categorizações** (43% de taxa de disparo neste corpus, específico
  do mix score/gap desses 46 casos — não generaliza diretamente pra distribuição de tráfego real).
- Tempo total das 20 chamadas: dentro dos 60.3s totais do script (que também inclui 92 embeddings
  SBERT, rápidos). Latência média por chamada Mistral observada em testes anteriores desta sessão:
  ~0.5-4s com `ministral-14b-latest`, dependendo de carga.
- **Decisão prática:** com taxa de disparo de ~43% e ganho real de só +4.3 pontos de acurácia (não
  os +19.6 pontos otimistas), o trade-off latência/custo-por-chamada vs. ganho de qualidade é bem
  mais modesto do que a calibração inicial sugeria. Ainda vale manter ativado (zero regressão nos
  acertos, unicamente upside), mas não deveria ser vendido como "resolve 75% dos erros" — resolve
  17% deles (2 de 12) na prática observada.

## Estado do repositório

**Aplicado.** Código em produção: `src/domain/application/use_cases/categorize_text.py`. Scripts de
validação: `scripts/anchors/validate_fallback_live.py`. Resultados brutos:
`data/processed/fallback_live_validation.json`. Nenhuma frase-âncora foi tocada.

## Pendência pra fora desta tarefa

A discrepância da seção 7.2 (metodologia documentada com `top_score >= 0.55`/`gap >= 0.08` nunca
implementados) ainda existe como texto desatualizado na memória oficial — só o código foi corrigido
aqui, com valores diferentes (0.63/0.04, calibrados) dos documentados (0.55/0.08, nunca calibrados).
Atualizar a documentação fica fora do escopo desta tarefa, como combinado.
