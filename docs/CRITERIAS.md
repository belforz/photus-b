
---

### Critérios de seleção por camada

**Camada 1 — Pureza semântica (eliminatório)**

A foto deve pertencer inequivocamente a uma única âncora. Se você olhar e hesitar entre duas âncoras, descarte. O teste prático: mostre para alguém sem contexto e peça para descrever a vibe em uma palavra. Se a palavra não converge com a âncora, descarte.

**Camada 2 — Origem da foto**

Prefira fotos produzidas intencionalmente para aquela estética em vez de fotos que acidentalmente se encaixam. Um fotógrafo que declarou "quero fazer low-key dramático" produziu algo mais puro do que uma foto subexposta por erro.

Fontes recomendadas por âncora:

| Âncora | Fonte ideal |
|---|---|
| Vitalidade | Getty Images → Sports, Unsplash → action |
| Solenidade | Portfolios de fotografia de produto/arquitetura |
| Conexão | Unsplash → portraits, faces |
| Distanciamento | 500px → dark/moody, Flickr grupos low-key |
| Simplicidade | VSCO feed, fotografia documental cotidiana |
| Conflito | Fotojornalismo urbano, Magnum Photos |
| Nostalgia | Flickr grupos film photography, VSCO vintage |
| Sublime | 500px → landscapes, National Geographic |
| Corporativo | LinkedIn stock, ShutterStock → headshots |
| Noturno | Flickr grupos nightlife, Getty → events |

**Camada 3 — Qualidade técnica mínima**

A foto precisa ser tecnicamente processável pelo Photus A. Requisitos mínimos:

```
resolução: ≥ 800×600 px
formato: JPG ou PNG sem compressão extrema
sem marca d'água sobreposta na área principal
sem bordas artificiais (molduras, polaroid fake)
sem filtros de app que alterem o espaço de cor (Instagram filters)
```

Esse último ponto é crítico: filtros de app podem elevar artificialmente grain ou saturação e contaminar as features de Nostalgia e Noturno especificamente.

**Camada 4 — Diversidade interna obrigatória**

Dentro de cada âncora, você precisa de variação para que o vetor de referência seja robusto e não enviesado por um único estilo de fotógrafo. Para cada âncora, o conjunto mínimo deve ter:

```
≥ 3 fotógrafos/fontes diferentes
≥ 2 condições de luz diferentes (quando aplicável)
≥ 2 composições diferentes (plano aberto e fechado)
sem fotos do mesmo evento/sessão
```

---

### Quantidade mínima por âncora

15 fotos é o mínimo para calcular média e desvio padrão com alguma confiança. 25–30 é o recomendado. Abaixo de 15 o desvio padrão vai ser instável e os intervalos do documento vão ter pouco respaldo empírico.

---

### Processo de delegação para outra pessoa

Se você for delegar a seleção, o briefing para cada âncora precisa ter três elementos, sem usar jargão técnico:

```
1. UMA frase descrevendo a vibe visual
2. DOIS exemplos de referência (links ou imagens)
3. DOIS exemplos de rejeição (o que NÃO é essa âncora)
```

Exemplo para Distanciamento:

```
VIBE: foto que passa solidão e frieza, como se a pessoa 
      fosse invisível no mundo.

ACEITAR:
  - pessoa de costas num corredor vazio e escuro
  - silhueta isolada numa paisagem urbana noturna sem pessoas

REJEITAR:
  - qualquer foto com mais de uma pessoa interagindo
  - escuro mas animado (festa, show) → isso é Noturno
  - escuro mas grandioso (montanha à noite) → isso é Sublime
```

Os exemplos de rejeição são mais importantes do que os de aceitação — eles ensinam as fronteiras entre âncoras vizinhas, que são exatamente onde a contaminação acontece.

---

### Registro obrigatório por foto selecionada

Para cada foto que entrar no conjunto, registre:

```json
{
  "filename": "dist_001.jpg",
  "anchor": "Distanciamento (Low-key)",
  "source": "500px",
  "photographer": "username_ou_nome",
  "reason_accepted": "corredor vazio, exposição baixa, sem pessoas",
  "diversity_tags": ["indoor", "artificial_light", "wide_shot"]
}
```

Esse registro vai virar seu dataset de calibração e eventualmente a seção de metodologia do artigo.

---

### O que fazer com as fotos descartadas

Não jogue fora. Fotos ambíguas que você descartou por pertencer a duas âncoras ao mesmo tempo são exatamente os casos de teste para o threshold — guarde em uma pasta separada `ambiguous/` e use depois para calibrar o gap mínimo do roteador semântico.