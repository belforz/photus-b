# Estrutura de Projeto - Sistema NLP de Classificação e Tagging

## Estrutura de Diretórios Proposta

```
photus-b/
│
├── docs/                                 # Documentação do projeto
│   ├── DESIGN_PATTERNS_NLP.md           # Análise de design patterns
│   ├── PROJECT_STRUCTURE.md             # Este arquivo
│   ├── API.md                           # Documentação da API
│   └── MODELS.md                        # Documentação dos modelos
│
├── src/
│   ├── domain/                          # Camada de domínio (lógica de negócio)
│   │   ├── __init__.py
│   │   ├── entities/                    # Entidades de domínio
│   │   │   ├── __init__.py
│   │   │   ├── classification.py       # Classification entity
│   │   │   ├── tag.py                   # Tag entity
│   │   │   ├── score.py                 # Score entity
│   │   │   ├── sentiment.py             # Sentiment entity
│   │   │   └── text_input.py            # TextInput entity
│   │   │
│   │   ├── value_objects/               # Value Objects (imutáveis)
│   │   │   ├── __init__.py
│   │   │   ├── confidence.py            # Confidence score (0-1)
│   │   │   ├── emotion_type.py          # Enum de tipos de emoção
│   │   │   ├── sentiment_type.py        # Enum de tipos de sentimento
│   │   │   └── technical_category.py    # Enum de categorias técnicas
│   │   │
│   │   ├── services/                    # Domain Services
│   │   │   ├── __init__.py
│   │   │   ├── classification_service.py
│   │   │   ├── scoring_service.py
│   │   │   └── sentiment_analyzer.py
│   │   │
│   │   └── interfaces/                  # Interfaces/Abstract base classes
│   │       ├── __init__.py
│   │       ├── classifier.py            # IClassifier interface
│   │       ├── embedder.py              # IEmbedder interface
│   │       ├── preprocessor.py          # IPreprocessor interface
│   │       ├── scorer.py                # IScorer interface
│   │       └── text_generator.py        # ITextGenerator interface
│   │
│   ├── application/                     # Camada de aplicação (use cases, orchestration)
│   │   ├── __init__.py
│   │   ├── use_cases/                   # Use cases do sistema
│   │   │   ├── __init__.py
│   │   │   ├── classify_text.py         # Use case: classificar texto
│   │   │   ├── analyze_sentiment.py     # Use case: analisar sentimento
│   │   │   ├── generate_tags.py         # Use case: gerar tags
│   │   │   └── batch_classify.py        # Use case: classificação em lote
│   │   │
│   │   ├── pipelines/                   # Pipelines de processamento
│   │   │   ├── __init__.py
│   │   │   ├── base_pipeline.py         # Pipeline base abstrato
│   │   │   ├── preprocessing_pipeline.py
│   │   │   ├── classification_pipeline.py
│   │   │   ├── scoring_pipeline.py
│   │   │   └── full_nlp_pipeline.py     # Pipeline completo end-to-end
│   │   │
│   │   ├── strategies/                  # Strategy implementations
│   │   │   ├── __init__.py
│   │   │   ├── classification/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── bert_classifier.py
│   │   │   │   ├── sentence_bert_classifier.py
│   │   │   │   └── hybrid_classifier.py
│   │   │   │
│   │   │   ├── embedding/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── sentence_bert_embedder.py
│   │   │   │   └── bert_embedder.py
│   │   │   │
│   │   │   └── scoring/
│   │   │       ├── __init__.py
│   │   │       ├── sentiment_scorer.py
│   │   │       ├── confidence_scorer.py
│   │   │       └── technical_scorer.py
│   │   │
│   │   ├── dto/                         # Data Transfer Objects
│   │   │   ├── __init__.py
│   │   │   ├── classification_request.py
│   │   │   ├── classification_response.py
│   │   │   └── batch_request.py
│   │   │
│   │   └── events/                      # Domain events (se usar Observer)
│   │       ├── __init__.py
│   │       ├── classification_completed.py
│   │       └── feedback_received.py
│   │
│   ├── infrastructure/                  # Camada de infraestrutura
│   │   ├── __init__.py
│   │   ├── adapters/                    # Adapters para bibliotecas externas
│   │   │   ├── __init__.py
│   │   │   ├── spacy_adapter.py         # Adapter para spaCy
│   │   │   ├── huggingface_adapter.py   # Adapter para HuggingFace (BERT)
│   │   │   └── mistral_adapter.py       # Adapter para Mistral API
│   │   │
│   │   ├── factories/                   # Factories para criação de objetos
│   │   │   ├── __init__.py
│   │   │   ├── model_factory.py         # Factory para modelos ML
│   │   │   ├── pipeline_factory.py      # Factory para pipelines
│   │   │   └── strategy_factory.py      # Factory para strategies
│   │   │
│   │   ├── repositories/                # Repositories para persistência
│   │   │   ├── __init__.py
│   │   │   ├── classification_repository.py
│   │   │   ├── model_repository.py
│   │   │   └── feedback_repository.py
│   │   │
│   │   ├── models/                      # Model wrappers e cache
│   │   │   ├── __init__.py
│   │   │   ├── bert_model.py
│   │   │   ├── sentence_bert_model.py
│   │   │   ├── spacy_model.py
│   │   │   └── model_cache.py           # Cache de modelos
│   │   │
│   │   ├── config/                      # Configuração
│   │   │   ├── __init__.py
│   │   │   ├── settings.py              # Settings usando pydantic
│   │   │   ├── model_config.py          # Configurações de modelos
│   │   │   └── pipeline_config.py       # Configurações de pipelines
│   │   │
│   │   └── persistence/                 # Storage implementations
│   │       ├── __init__.py
│   │       ├── database.py              # Database connection
│   │       ├── cache.py                 # Redis/memcache
│   │       └── file_storage.py          # File-based storage
│   │
│   ├── presentation/                    # Camada de apresentação (API, CLI)
│   │   ├── __init__.py
│   │   ├── api/                         # REST API
│   │   │   ├── __init__.py
│   │   │   ├── v1/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── routes/
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── classification.py
│   │   │   │   │   ├── sentiment.py
│   │   │   │   │   └── health.py
│   │   │   │   │
│   │   │   │   └── schemas/             # Pydantic schemas
│   │   │   │       ├── __init__.py
│   │   │   │       ├── request.py
│   │   │   │       └── response.py
│   │   │   │
│   │   │   ├── dependencies.py          # FastAPI dependencies
│   │   │   ├── middleware.py
│   │   │   └── app.py                   # FastAPI app instance
│   │   │
│   │   └── cli/                         # Command-line interface
│   │       ├── __init__.py
│   │       ├── commands/
│   │       │   ├── __init__.py
│   │       │   ├── classify.py
│   │       │   └── train.py
│   │       └── main.py
│   │
│   └── shared/                          # Código compartilhado
│       ├── __init__.py
│       ├── exceptions.py                # Exceções customizadas
│       ├── logging.py                   # Logging utilities
│       ├── metrics.py                   # Metrics collection
│       └── utils.py                     # Utility functions
│
├── tests/                               # Testes
│   ├── __init__.py
│   ├── unit/                            # Testes unitários
│   │   ├── __init__.py
│   │   ├── domain/
│   │   ├── application/
│   │   └── infrastructure/
│   │
│   ├── integration/                     # Testes de integração
│   │   ├── __init__.py
│   │   ├── test_pipelines.py
│   │   └── test_api.py
│   │
│   ├── e2e/                            # Testes end-to-end
│   │   ├── __init__.py
│   │   └── test_full_flow.py
│   │
│   ├── fixtures/                        # Test fixtures
│   │   ├── __init__.py
│   │   ├── sample_texts.py
│   │   └── mock_models.py
│   │
│   └── conftest.py                      # Pytest configuration
│
├── notebooks/                           # Jupyter notebooks (experimentação)
│   ├── 01_data_exploration.ipynb
│   ├── 02_model_evaluation.ipynb
│   └── 03_pipeline_testing.ipynb
│
├── data/                                # Dados
│   ├── raw/                             # Dados brutos
│   ├── processed/                       # Dados processados
│   ├── models/                          # Modelos salvos
│   │   ├── bert/
│   │   ├── sentence-bert/
│   │   └── spacy/
│   └── embeddings/                      # Cache de embeddings
│
├── scripts/                             # Scripts utilitários
│   ├── download_models.py               # Download de modelos
│   ├── setup_database.py                # Setup de database
│   └── benchmark.py                     # Benchmark de performance
│
├── config/                              # Arquivos de configuração
│   ├── development.yaml
│   ├── production.yaml
│   └── test.yaml
│
├── deployment/                          # Deployment configs
│   ├── docker/
│   │   ├── Dockerfile
│   │   └── docker-compose.yml
│   ├── kubernetes/
│   │   ├── deployment.yaml
│   │   └── service.yaml
│   └── terraform/
│
├── .env.example                         # Exemplo de variáveis de ambiente
├── .gitignore
├── .dockerignore
├── pyproject.toml                       # Poetry/pip configuration
├── poetry.lock
├── requirements.txt
├── README.md
├── LICENSE
└── Makefile                             # Comandos úteis

```

---

## Descrição Detalhada das Camadas

### 1. Domain Layer (`src/domain/`)

**Responsabilidade**: Lógica de negócio pura, independente de frameworks.

#### Entities (`entities/`)
- **Propósito**: Objetos com identidade única
- **Exemplos**:
  - `Classification`: Representa uma classificação completa
  - `Tag`: Uma tag aplicada ao texto
  - `Score`: Pontuação de algum aspecto
  - `Sentiment`: Sentimento identificado
  - `TextInput`: Input do usuário

#### Value Objects (`value_objects/`)
- **Propósito**: Objetos imutáveis definidos por seus valores
- **Exemplos**:
  - `Confidence`: Score de confiança (0.0-1.0)
  - `EmotionType`: Enum (ALEGRIA, TRISTEZA, RAIVA, etc.)
  - `SentimentType`: Enum (POSITIVO, NEGATIVO, NEUTRO)
  - `TechnicalCategory`: Categorias técnicas do domínio

#### Services (`services/`)
- **Propósito**: Operações de domínio que não pertencem a uma entidade
- **Exemplos**:
  - `ClassificationService`: Lógica de classificação
  - `ScoringService`: Lógica de pontuação
  - `SentimentAnalyzer`: Análise de sentimento

#### Interfaces (`interfaces/`)
- **Propósito**: Contratos que infraestrutura deve implementar
- **Exemplos**:
  - `IClassifier`: Interface para classificadores
  - `IEmbedder`: Interface para geradores de embeddings
  - `IPreprocessor`: Interface para preprocessadores

---

### 2. Application Layer (`src/application/`)

**Responsabilidade**: Orquestração, use cases, fluxo de aplicação.

#### Use Cases (`use_cases/`)
- **Propósito**: Casos de uso do sistema
- **Padrão**: Um arquivo por use case
- **Exemplos**:
  - `classify_text.py`: Classificar um texto
  - `analyze_sentiment.py`: Analisar sentimento
  - `generate_tags.py`: Gerar tags
  - `batch_classify.py`: Classificação em lote

#### Pipelines (`pipelines/`)
- **Propósito**: Implementação do Pipeline Pattern
- **Estrutura**:
  - `base_pipeline.py`: Classe abstrata base
  - Pipelines específicos herdam da base
- **Exemplos**:
  - `preprocessing_pipeline.py`: Limpeza, normalização
  - `classification_pipeline.py`: Classificação
  - `full_nlp_pipeline.py`: Pipeline completo

#### Strategies (`strategies/`)
- **Propósito**: Implementação do Strategy Pattern
- **Organização**: Por tipo de estratégia
- **Exemplos**:
  - `classification/bert_classifier.py`
  - `embedding/sentence_bert_embedder.py`
  - `scoring/confidence_scorer.py`

#### DTOs (`dto/`)
- **Propósito**: Objetos para transferência de dados entre camadas
- **Exemplos**:
  - `ClassificationRequest`: Dados de entrada
  - `ClassificationResponse`: Dados de saída
  - `BatchRequest`: Requisição em lote

---

### 3. Infrastructure Layer (`src/infrastructure/`)

**Responsabilidade**: Implementações concretas, acesso a recursos externos.

#### Adapters (`adapters/`)
- **Propósito**: Adapter Pattern para bibliotecas externas
- **Exemplos**:
  - `spacy_adapter.py`: Wrapper para spaCy
  - `huggingface_adapter.py`: Wrapper para BERT
  - `mistral_adapter.py`: Wrapper para API Mistral

#### Factories (`factories/`)
- **Propósito**: Factory Pattern para criação de objetos
- **Exemplos**:
  - `model_factory.py`: Cria e cacheia modelos
  - `pipeline_factory.py`: Cria pipelines configurados
  - `strategy_factory.py`: Cria strategies

#### Repositories (`repositories/`)
- **Propósito**: Repository Pattern para persistência
- **Exemplos**:
  - `classification_repository.py`: Salva/carrega classificações
  - `model_repository.py`: Gerencia modelos
  - `feedback_repository.py`: Gerencia feedback

#### Models (`models/`)
- **Propósito**: Wrappers para modelos ML
- **Inclui**: Cache, lazy loading, model management

#### Config (`config/`)
- **Propósito**: Configuração centralizada
- **Usa**: Pydantic Settings
- **Exemplos**:
  - `settings.py`: Settings principais
  - `model_config.py`: Configuração de modelos
  - `pipeline_config.py`: Configuração de pipelines

---

### 4. Presentation Layer (`src/presentation/`)

**Responsabilidade**: Interface com mundo externo (API, CLI).

#### API (`api/`)
- **Framework**: FastAPI
- **Estrutura**:
  - Versionamento (`v1/`)
  - Routes separadas por recurso
  - Schemas Pydantic para validação
  - Middleware para logging, auth, etc.

#### CLI (`cli/`)
- **Framework**: Click ou Typer
- **Propósito**: Interface de linha de comando
- **Comandos**: classify, batch, train, evaluate

---

### 5. Shared (`src/shared/`)

**Responsabilidade**: Código compartilhado entre camadas.

- `exceptions.py`: Exceções customizadas
- `logging.py`: Configuração de logging
- `metrics.py`: Coleta de métricas
- `utils.py`: Funções utilitárias

---

## Fluxo de Dependências

```
Presentation → Application → Domain ← Infrastructure
                                ↑
                                │
                         (implements interfaces)
```

**Regras**:
1. Domain não depende de nada
2. Application depende apenas de Domain
3. Infrastructure implementa interfaces de Domain
4. Presentation usa Application

---

## Arquivos de Configuração Essenciais

### `pyproject.toml`
```toml
[tool.poetry]
name = "photus-b"
version = "0.1.0"
description = "Sistema NLP de classificação e tagging"

[tool.poetry.dependencies]
python = "^3.10"
transformers = "^4.35.0"
sentence-transformers = "^2.2.0"
spacy = "^3.7.0"
torch = "^2.1.0"
fastapi = "^0.104.0"
uvicorn = "^0.24.0"
pydantic = "^2.5.0"
pydantic-settings = "^2.1.0"

[tool.poetry.dev-dependencies]
pytest = "^7.4.0"
pytest-asyncio = "^0.21.0"
black = "^23.11.0"
mypy = "^1.7.0"
ruff = "^0.1.0"
```

### `.env.example`
```ini
# Environment
ENVIRONMENT=development

# API
API_HOST=0.0.0.0
API_PORT=8000

# Models
SENTENCE_BERT_MODEL=all-MiniLM-L6-v2
BERT_MODEL=bert-base-uncased
SPACY_MODEL=pt_core_news_lg
MISTRAL_API_KEY=your_key_here

# Cache
REDIS_URL=redis://localhost:6379

# Database
DATABASE_URL=postgresql://user:pass@localhost/photus

# Logging
LOG_LEVEL=INFO
```

### `Makefile`
```makefile
.PHONY: install test lint format run docker-build

install:
	poetry install

test:
	poetry run pytest tests/ -v

lint:
	poetry run ruff check src/
	poetry run mypy src/

format:
	poetry run black src/ tests/

run:
	poetry run uvicorn src.presentation.api.app:app --reload

docker-build:
	docker-compose build

docker-up:
	docker-compose up -d
```

---

## Benefícios desta Estrutura

### ✅ Separação de Responsabilidades
Cada camada tem papel bem definido e não invade outras.

### ✅ Testabilidade
- Domain: testes puros, sem dependências
- Application: testes com mocks de infraestrutura
- Infrastructure: testes de integração

### ✅ Manutenibilidade
Mudanças em uma camada não afetam outras (desde que interfaces sejam mantidas).

### ✅ Escalabilidade
Fácil adicionar novos modelos, pipelines, estratégias sem refatoração massiva.

### ✅ Extensibilidade
Adicionar features novas é plug-and-play seguindo os patterns existentes.

### ✅ DDD-Friendly
Segue princípios de Domain-Driven Design, facilitando evolução do domínio.

### ✅ Clean Architecture
Dependências apontam para dentro (Domain é independente).

---

## Próximos Passos para Implementação

### Fase 1: Setup Básico
1. Criar estrutura de diretórios
2. Setup `pyproject.toml` e dependências
3. Configurar `.env` e `settings.py`
4. Setup básico de logging

### Fase 2: Domain Layer
1. Definir entities principais
2. Criar value objects
3. Definir interfaces

### Fase 3: Infrastructure Layer
1. Implementar adapters (spaCy, BERT, Mistral)
2. Criar model factory
3. Setup model cache

### Fase 4: Application Layer
1. Implementar pipelines básicos
2. Criar strategies de classificação
3. Implementar use cases principais

### Fase 5: Presentation Layer
1. Setup FastAPI
2. Criar rotas principais
3. Implementar CLI básico

### Fase 6: Testing & Deployment
1. Escrever testes
2. Setup Docker
3. CI/CD pipeline
4. Documentação

---

## Convenções de Código

### Naming
- **Classes**: PascalCase (`TextClassifier`)
- **Functions/Methods**: snake_case (`classify_text()`)
- **Constants**: UPPER_SNAKE_CASE (`MAX_TOKENS`)
- **Private**: prefixo underscore (`_internal_method()`)

### Type Hints
```python
def classify_text(text: str, model: IClassifier) -> Classification:
    ...
```

### Docstrings
```python
def classify_text(text: str) -> Classification:
    """Classifica um texto em categorias técnicas.
    
    Args:
        text: Texto a ser classificado
        
    Returns:
        Classification object com resultados
        
    Raises:
        ValueError: Se texto for vazio
    """
```

### Imports
```python
# Standard library
import os
from typing import List, Dict

# Third-party
import torch
from fastapi import FastAPI

# Local
from src.domain.entities import Classification
from src.application.pipelines import ClassificationPipeline
```

---

## Recursos Adicionais

### Ferramentas Recomendadas
- **Linting**: Ruff (rápido) ou Pylint
- **Formatting**: Black
- **Type Checking**: mypy
- **Testing**: pytest + pytest-cov
- **Documentation**: Sphinx ou MkDocs
- **API Docs**: FastAPI built-in (Swagger/ReDoc)

### CI/CD
- **GitHub Actions** ou **GitLab CI**
- Passos: lint → test → build → deploy

### Monitoramento
- **Logging**: structlog
- **Metrics**: Prometheus
- **Tracing**: OpenTelemetry
- **Dashboards**: Grafana

---

