# Fallback técnico: `null_reason` estruturado + tratamento de erro em `call_mistral_technical`

Duas mudanças relacionadas em `call_mistral_technical` (rota `__tecnico__`, prompt `technical.md`):
(1) o prompt ganhou um campo `null_reason` estruturado pra distinguir por que o LLM devolveu
`anchor: null`, e (2) a função ganhou recuperação de erro de parse, que ela não tinha antes,
reaproveitando o padrão já existente em `call_semantic_fallback`.

## Contexto

Ao testar o caminho técnico da API (`/v1/categorize`) com `"produto isolado em fundo branco"` —
caso documentado de colisão com a âncora `__tecnico__` — o prompt técnico (recém-reescrito, v1.2)
corretamente reconheceu a suspeita de falso positivo de roteamento e devolveu `anchor: null` com uma
explicação em `reasoning`. Mas antes de decidir usar esse sinal pra reverter automaticamente a
`category`, dois problemas precisavam ser resolvidos:

1. **`anchor: null` era ambíguo.** O prompt v1.2 tinha três regras (3, 5, 6) que todas podiam
   devolver `anchor: null`, por motivos opostos: suspeita de misroute (reverter faz sentido),
   ambiguidade genuína entre âncoras (reverter não resolve nada — o pedido é realmente ambíguo), e
   confiança baixa (idem). `reasoning` é texto livre, não confiável pra decisão de código. Sem
   separar isso, qualquer lógica de "null → recalcula categoria" arriscava forçar uma âncora em cima
   de casos que deveriam ficar genuinamente indefinidos — regressão disfarçada de correção.
2. **Sem tratamento de erro no parse.** Diferente de `call_semantic_fallback` — que já tinha
   recuperação quando o LLM foge do formato esperado (visto em produção: um caso retornou
   `anchor: "AMBÍGUO"`, o parse falhou, e o código logou warning e manteve o top-1 do SBERT) —
   `call_mistral_technical` não tinha nenhuma tentativa de parse, então não tinha como logar nem se
   recuperar de uma resposta fora do formato.

## O que foi implementado

### 1. `prompts/technical.md` v1.2 → v1.3

Novo campo `null_reason` no schema de saída, com três valores possíveis, um por regra:

| `null_reason` | Regra | Significado |
|---|---|---|
| `misroute_suspected` | 3 | Roteamento pro `__tecnico__` provavelmente errado — nenhum parâmetro técnico manipulável real, é descrição de cena pura. |
| `ambiguous` | 5 | Parâmetro genuinamente técnico, mas compatível com mais de uma âncora — não é erro de roteamento. |
| `low_confidence` | 6 | Técnico genuíno, mas faltam elementos pra mapear com segurança. |

`null_reason` só é preenchido quando `anchor` vem `null`; quando `anchor` tem um valor, `null_reason`
deve vir `null`. Isso é o único campo pensado pra decisão de código — os demais (`intention`,
`attributes`, `reasoning`) continuam só diagnóstico/auditoria, sem uso automatizado.

### 2. `call_mistral_technical` (`categorize_text.py`) — parse com recuperação

Reaproveita `_parse_json_object` (mesmo helper de `call_semantic_fallback`, zero lógica nova
duplicada). Mudou de retornar `Optional[str]` pra `Optional[dict]`:

```python
{"raw": <string bruta da resposta>, "null_reason": <str | None>}
```

Se o parse falhar (JSON malformado, truncado, ou resposta sem JSON nenhum), loga
`[step 4/4] could not parse Mistral JSON response: {resposta bruta!r}` e degrada pra
`null_reason=None` — **nunca propaga exceção**. `category`/`category_code` nunca dependeram desse
parse (sempre vieram do ranking SBERT), então uma falha aqui não afeta o resultado principal, só o
campo diagnóstico.

### 3. `CategoryResult.technical_null_reason` (novo campo)

Populado em `categorize()` a partir do dict acima. Incluído em `to_dict()` e no schema da API
(`CategorizeResponse.technical_null_reason`). **Puramente diagnóstico agora** — não há nenhum
código que leia esse campo pra corrigir `category` automaticamente. Essa decisão foi adiada de
propósito: reverter a categoria com base em `misroute_suspected` só faz sentido calibrado contra um
corpus de casos confirmados, e hoje existe só **n=1** confirmado
(`"produto isolado em fundo branco"`) — o mesmo tipo de intuição que a calibração do threshold de
fallback semântico (`CALIBRACAO_THRESHOLD_MISTRAL.md`) já mostrou que erra por margem grande quando
feita sem dados (projeção otimista 93.5% vs. real 78.3%, -15.2 pontos).

### 4. Bug lateral corrigido: schema quebrado

`src/presentation/api/v1/schemas/classification.py` tinha um erro de sintaxe introduzido ao expor
os campos de auditoria (`sbert_anchor_before_fallback = Optional[str] = None`, sem `:` — chained
assignment inválido, `TypeError: '_SpecialForm' object does not support item assignment` no import).
Isso quebrava o import do módulo inteiro, ou seja, a API não subia. Corrigido pra anotação de tipo
correta antes de qualquer teste.

## Validação

### Recuperação de erro (respostas sintéticas malformadas, via monkeypatch de `LLMConnector.send_message`)

| Resposta simulada | Resultado |
|---|---|
| Texto solto sem JSON (`"Desculpe, não entendi..."`) | Warning logado com a resposta bruta, sem exceção, `category="__tecnico__"`, `technical_null_reason=None` |
| JSON com fence aberto e nunca fechado (truncado) | Mesmo resultado — warning + degradação graciosa |

### Caminho feliz — 4 casos originais + 8 casos adicionais (`scripts/validate_tecnical_.py`, chamadas reais)

Nenhum dos 12 casos technical-triggering quebrou ou precisou do tratamento de erro — todos
retornaram JSON válido. Achados:

| Caso | `technical` | `category` final | `null_reason` | Nota |
|---|---|---|---|---|
| `f/1.4, deixa o fundo borrado` | True | `__tecnico__` | `None` | técnico puro sem contexto — ver limitação abaixo |
| `f/1.2, still life de produto...` | True | `__tecnico__` | **`low_confidence`** | ✅ bate com Regra 6 |
| `softbox, luz difusa...` | True | `__tecnico__` | `None` (anchor preenchido) | ✅ correto |
| `compensação de exposição +1.5...` | False | `__tecnico__` | `None` | nem chamou o LLM |
| `f/1.4, ISO 3200... silhueta na porta, sozinha` | True | `__tecnico__` | `None` (anchor=Distanciamento) | LLM resolveu certo internamente, mas `category` não é sobrescrita (limitação conhecida) |
| `f/1.2... catchlight... bem de perto` | True | `__tecnico__` | `None` (anchor=Conexão) | idem |
| `compensação -2 stops... pessoa sozinha e isolada` | True | **Distanciamento** | `None` (anchor=Distanciamento) | aqui `category` bateu com o LLM por coincidência — `__tecnico__` passou do threshold mas não era o top1 do SBERT |
| `bracketing de exposição... dynamic range da montanha` | False | Sublime | — | não técnico, resolvido só por SBERT |
| `push processing +2 stops... foto de décadas` | False | Nostalgia | — | não técnico; resolvido pelo **fallback semântico** (não o técnico), reasoning cita grão/textura analógica corretamente |
| `softbox a 45°... retrato de LinkedIn` | True | `__tecnico__` | `None` (anchor=Corporativo) | LLM resolveu certo internamente, `category` não sobrescrita |
| `flash sincronização lenta... pista de dança` | False | Noturno | — | fallback semântico resolveu certo (SBERT top1 antes do fallback era `__tecnico__`, mas com score baixo) |
| `ajusta o negativo pra ficar mais cru` | False | Corporativo | — | fallback semântico não resolveu (reasoning ambíguo entre Nostalgia e "vintage falso"), manteve SBERT top1 |

Nenhum dos 12 casos exercitou `misroute_suspected` ou `ambiguous` — só o `low_confidence` já visto
antes se repetiu. O corpus de `null_reason` continua pequeno; não é evidência suficiente pra calibrar
nada ainda, só confirma que o parse novo não introduziu regressão no caminho feliz.

## Limitações conhecidas (não corrigidas nesta tarefa, fora de escopo)

- **`category` nunca é corrigida a partir do diagnóstico técnico**, mesmo quando o LLM identifica
  corretamente a âncora certa (`Distanciamento`, `Conexão`, `Corporativo` nos casos acima) ou marca
  `misroute_suspected`. A colisão upstream com `__tecnico__` (score SBERT) continua determinando
  `category` sozinha. Decisão de arquitetura pendente, discutida mas não implementada — precisa de
  corpus maior antes de calibrar qualquer piso de confiança pra reversão automática.
- **Lacuna no enum do `null_reason`**: casos "técnico puro, sem nenhum contexto de cena mapeável"
  (ex. `"f/1.4, deixa o fundo borrado"`) devolvem `anchor: null` e `null_reason: null` juntos — não é
  misroute, nem ambíguo, nem baixa confiança, só não há âncora nenhuma pra mapear. As 3 regras atuais
  não cobrem esse caso explicitamente. Não é bug do tratamento de erro, é lacuna de cobertura do
  prompt — registrado aqui, não corrigido.

## Estado do repositório

**Aplicado, não commitado.** Arquivos alterados: `src/domain/application/use_cases/categorize_text.py`
(`call_mistral_technical` reescrita, `CategoryResult.technical_null_reason` novo),
`src/infrastructure/config/prompts/technical.md` (v1.3), `src/presentation/api/v1/schemas/classification.py`
(campo novo + bug de sintaxe corrigido). Nenhuma âncora ou threshold foi tocado.
