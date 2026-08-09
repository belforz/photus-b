# API — Photus B

O `main.py` na raiz do projeto sobe um servidor HTTP (FastAPI + Uvicorn) que expõe a categorização semântica do Photus B. Ele recebe uma frase em linguagem natural e devolve a âncora de conhecimento mais próxima, para ser consumida por outro serviço (ex.: Photus A).

## Rodando o servidor

```bash
uv run main.py
```

Variáveis de ambiente opcionais:

| Variável | Padrão | Descrição |
|---|---|---|
| `HOST` | `0.0.0.0` | Interface de bind do servidor |
| `PORT` | `8000` | Porta HTTP |
| `RELOAD` | `false` | `true` ativa auto-reload (uvicorn) para desenvolvimento |

Requer `.env` com `MISTRAL_API_KEY` e `HF_API_KEY` (ver `.env-example.md`). Sem `MISTRAL_API_KEY` válida o serviço continua funcionando normalmente — apenas o fallback de inputs técnicos para o Mistral fica desabilitado (loga aviso e `mistral_response` volta `null`).

Na inicialização (`lifespan` do FastAPI), o modelo de embeddings (`paraphrase-multilingual-MiniLM-L12-v2`) e o grafo de âncoras (`data/raw/knowledge_anchors.json`) são carregados **uma única vez** em memória e reutilizados por todas as requisições — evita recarregar o modelo (~segundos) a cada chamada.

## Endpoints

### `GET /health`

Healthcheck simples.

```json
{ "status": "ok" }
```

`status` é `"starting"` enquanto o modelo ainda está sendo carregado.

### `POST /v1/categorize`

Categoriza uma frase.

**Request**

```json
{ "text": "mostre a melhor foto melancolica" }
```

| Campo | Tipo | Obrigatório |
|---|---|---|
| `text` | string | sim, não pode ser vazio |

**Response — 200**

```json
{
  "input_text": "mostre a melhor foto melancolica",
  "category": "Conexão",
  "category_code": "conexao",
  "confidence": 0.5831145644187927,
  "technical": false,
  "technical_score": 0.2785519063472748,
  "threshold": 0.48,
  "top_matches": [
    { "anchor_id": "Conexão (Close-up)", "anchor_phrase": "foto de rosto humano em plano fechado...", "score": 0.5831145644187927 }
  ],
  "mistral_response": null
}
```

| Campo | Descrição |
|---|---|
| `category` | Rótulo legível da âncora vencedora, sem o parêntese descritivo (`"Conexão"`, não `"Conexão (Close-up)"`) |
| `category_code` | Versão *slug* de `category`, ascii/snake_case, estável para integração (`"conexao"`) |
| `confidence` | Similaridade de cosseno (0–1) entre o embedding do texto e a âncora vencedora |
| `technical` | `true` se o texto foi classificado como pedido técnico (parâmetros de câmera/fotografia) |
| `technical_score` | Score de similaridade com a âncora `__tecnico__`, ou `1.0` se um parâmetro técnico explícito foi detectado por regex (ex.: `f/2.8`, `ISO 800`) |
| `threshold` | Limiar usado para decidir `technical` (constante `THRESHOLD_TECNICO = 0.48`) |
| `top_matches` | As 5 âncoras mais próximas, para debug/observabilidade |
| `mistral_response` | Preenchido apenas quando `technical=true`: resposta do Mistral usando o prompt `base`. `null` se não técnico ou se o fallback está desabilitado |

**Response — 400** (texto vazio)

```json
{ "detail": [{ "type": "string_too_short", "loc": ["body", "text"], "msg": "String should have at least 1 character" }] }
```

**Response — 503** — serviço ainda inicializando (modelo carregando).

**Response — 500** — erro inesperado ao categorizar (ver logs do servidor).

## Arquitetura

A lógica de categorização (ranquear âncoras por cosseno, detectar input técnico, acionar fallback do Mistral) mora em `src/domain/application/use_cases/categorize_text.py` (`CategorizationService`), usada tanto pela API (`src/presentation/api/`) quanto pelo script de CLI `scripts/anchors/run_custom_sentences.py` — para as duas pontas nunca divergirem na forma de decidir uma categoria.

```
main.py                                    → sobe o uvicorn, aponta pra presentation/api/app.py
src/presentation/api/app.py                → FastAPI app + lifespan (carrega o modelo 1x)
src/presentation/api/v1/routes/classification.py → rota POST /v1/categorize
src/presentation/api/v1/schemas/classification.py → schemas Pydantic de request/response
src/domain/application/use_cases/categorize_text.py → CategorizationService (regra de negócio)
```
