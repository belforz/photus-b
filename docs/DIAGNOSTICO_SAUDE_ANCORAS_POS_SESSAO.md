# Diagnóstico de Saúde das Âncoras — Comparativo Antes/Depois da Sessão Completa

Nenhuma frase foi editada nesta tarefa — só reexecução do diagnóstico original
(`scripts/anchors/diagnose_router_health.py`, mesmo corpus de 51 casos: Grupo A=30, B=16, C=5)
contra o estado atual das âncoras. "Antes" = números publicados em `DIAGNOSTICO_SAUDE_ANCORAS.md`
(baseline pré-sessão, 49 frases). "Depois" = estado atual, pós-rodada-5, **54 frases** (49 + 5 líquidas:
+2 Corporativo r1, +1 Conexão r4, +1 Solenidade r5, +1 Conflito r5 líquido — Simplicidade voltou a 4
porque a r3 foi revertida, Corporativo voltou a 5 porque a r2 foi revertida, `__tecnico__` continua
com 9 frases, mas 8 delas foram reescritas de lista de palavras-chave pra prosa na r1).

Resultados brutos desta rodada: `data/processed/router_health_diag_results.json`.

## 1. Grupo A — casos centrais, por âncora

| Âncora | score médio antes | score médio depois | gap médio antes | gap médio depois | acerto antes | acerto depois |
|---|---|---|---|---|---|---|
| Vitalidade (Ação) | 0.575 | 0.575 | 0.083 | 0.083 | 3/3 | 3/3 |
| Solenidade (Estase) | 0.618 | 0.618 | 0.054 | 0.054 | 2/3 | 2/3 |
| Conexão (Close-up) | 0.666 | 0.666 | 0.141 | 0.141 | 2/3 | 2/3 |
| Distanciamento (Low-key) | 0.666 | 0.666 | 0.065 | 0.065 | 2/3 | 2/3 |
| Simplicidade (Cotidiano) | 0.468 | 0.468 | 0.037 | 0.028 | 2/3 | 2/3 |
| Conflito (Caos) | 0.615 | 0.615 | 0.123 | 0.123 | 2/3 | 2/3 |
| Nostalgia (Analógico) | 0.600 | 0.600 | 0.119 | 0.105 | 1/3 | 1/3 |
| Sublime (Paisagem) | 0.701 | 0.701 | 0.280 | 0.280 | 3/3 | 3/3 |
| **Corporativo (Focado)** | **0.534** | **0.553** | 0.039 | 0.038 | **1/3** | **3/3** |
| Noturno (Festa) | 0.594 | 0.594 | 0.094 | 0.094 | 3/3 | 3/3 |

**Achado principal do Grupo A: Corporativo (Focado) foi a única âncora cujos 3 casos centrais
mudaram de resultado** — 1/3 → 3/3 acerto, e `low_confidence` caiu de 2/3 para 0/3 (não está na
tabela acima, mas é o mesmo padrão já documentado na rodada 1). As outras 9 âncoras têm o **score
médio e acerto idênticos** — pequenas variações de gap médio (Simplicidade, Nostalgia) são efeito
colateral de outras âncoras mudando de score no ranking geral, não mudança de comportamento das
próprias âncoras (nenhuma das duas foi tocada em nenhuma rodada).

**Achado à parte, não causado por esta sessão:** o caso central `"produto isolado em fundo branco"`
(Grupo A de Solenidade) já roteava para `__tecnico__` (0.511) na baseline pré-sessão — confirmado
rodando o backup do estado original (`knowledge_anchors_before.json`). A frase de `__tecnico__`
responsável (`"deixa o fundo borrado, fundo sumiu..."`) nunca foi alterada em nenhuma rodada; é a
mesma frase desde antes desta sessão. Isso já estava embutido no `score médio=0.618` original — não
é uma regressão desta sessão, só não tinha sido isolado como causa específica no relatório original.

## 2. Grupo B (fronteira) — 5/16 (31%) → 7/16 (44%)

| Métrica | Antes | Depois |
|---|---|---|
| Acertou a âncora esperada | 5/16 (31%) | **7/16 (44%)** |
| Caiu na armadilha documentada | 9/16 (56%) | 7/16 (44%) |
| Foi pra uma terceira âncora | 2/16 (13%) | 2/16 (13%) |

### Os 2 casos que viraram de TRAP/OUTRA para HIT

| Caso | Antes | Depois |
|---|---|---|
| `"cena doméstica mas visivelmente produzida e estilizada"` | TRAP → Simplicidade | **HIT → Solenidade 0.700** |
| `"cena social mas estática e formal, tipo coquetel corporativo"` | HIT já era esperado? não — era caso de fronteira, ver nota | HIT → Corporativo 0.655 |

Nota: `"cena social mas estática e formal, tipo coquetel corporativo"` já não era mais TRAP desde a
rodada 1 (era o próprio caso-alvo de Corporativo r1); confirmado aqui de novo só como checagem de
regressão — segue correto.

O ganho líquido real do Grupo B é **o caso de Solenidade** (rodada 5) — o único caso de fronteira
que efetivamente mudou de categoria (TRAP→HIT) nesta comparação, validando que a frase nova de
Solenidade generaliza para o corpus oficial, não só para o caso de teste customizado.

### Os 7 casos que continuam em TRAP (inalterados)

Nenhum dos 7 traps restantes mudou de resultado. Vale destacar 3 que **têm relação direta com
trabalho feito nesta sessão mas usam frase diferente da testada nos rounds**, mostrando que os
ajustes não generalizaram totalmente para variações de fraseado:

| Caso (Grupo B oficial) | Esperado | Ainda cai em | Nota |
|---|---|---|---|
| `"retrato próximo e emotivo em ambiente de estúdio formal"` | Conexão | Corporativo 0.706 | Rodada 1/4 corrigiu `"retrato de estúdio emotivo, com olhar vivo"` (fraseado ligeiramente diferente) — este, do corpus oficial, não se beneficiou |
| `"pessoa em roupa profissional mas em ambiente real, não estúdio"` | Simplicidade | Corporativo 0.666 | Limitação conhecida, fechada formalmente na rodada 4 |
| `"rosto pequeno e dividido em meio a uma multidão"` | Conflito | Conexão 0.624 | Limitação conhecida, fechada na rodada 5 (a frase que resolvia causava regressão em Noturno e foi revertida) |

Os outros 4 traps (`"atleta com expressão de dor extrema..."` → Vitalidade, `"estética vintage só
que digitalmente perfeita..."` → Nostalgia, `"paisagem grandiosa mas fotografada no escuro"` →
Sublime, `"pessoa sozinha ao entardecer, sombras longas"` → Distanciamento) nunca foram alvo de
nenhuma rodada desta sessão — inalterados, como esperado.

## 3. Grupo C (técnico) — 1/5 (20%) → 4/5 (80%)

| Caso | Antes (technical) | Depois (technical) |
|---|---|---|
| `"f/1.8, ISO 800, 1/500s"` | True (regex) | True (regex, inalterado) |
| `"deixa o fundo borrado e o rosto nítido"` | False (0.446) | **True (0.499)** |
| `"profundidade de campo rasa"` | False (0.459) | **True (0.671)** |
| `"subexposição intencional em low-key"` | False (0.402) | False (0.293) — **ainda falha** |
| `"estoure o brilho dos realces"` | False (0.432) | **True (0.535)** |

4 de 5 casos técnicos agora são detectados via **score semântico** (não só regex) — resultado direto
da reescrita de 8 das 9 frases de `__tecnico__` na rodada 1, que trocou listas de palavras-chave por
prosa natural. O único caso que permanece falhando (`"subexposição intencional em low-key"`) é o
mesmo documentado desde a rodada 1 como não resolvido pela reescrita de frases — a ambiguidade com o
nome técnico da âncora Distanciamento (`low-key`) continua puxando o score pra baixo do threshold.

## 4. Classificação de saúde — o que mudou de categoria

| Âncora | Antes | Depois | Mudou? |
|---|---|---|---|
| Sublime (Paisagem) | ✅ Saudável | ✅ Saudável | Não |
| **Corporativo (Focado)** | 🔴 Defasada | **🟡 Saudável com ressalva** | **Sim — subiu 2 níveis** |
| **`__tecnico__`** | 🔴 Muito defasada | **🟡 Saudável com ressalva** | **Sim — subiu 2 níveis** |
| **Solenidade (Estase)** | 🟠 Defasada | **🟡 Defasada parcial** | **Sim — subiu 1 nível** |
| Vitalidade (Ação) | 🟡 Saudável com ressalva | 🟡 Saudável com ressalva | Não |
| Noturno (Festa) | 🟡 Saudável com ressalva | 🟡 Saudável com ressalva | Não (sobreviveu a um quase-incidente na rodada 5, revertido a tempo) |
| Conexão (Close-up) | 🟡 Defasada parcial | 🟡 Defasada parcial | Não (casos customizados corrigidos, mas o caso oficial do Grupo B com fraseado diferente não generalizou) |
| Conflito (Caos) | 🟠 Defasada | 🟠 Defasada | Não (rodada 5 tentou, revertida parcialmente; nenhum dos 2 problemas documentados foi resolvido no corpus oficial) |
| Distanciamento (Low-key) | 🟠 Defasada | 🟠 Defasada | Não (nunca tocada) |
| Nostalgia (Analógico) | 🔴 Defasada | 🔴 Defasada | Não (nunca tocada) |
| Simplicidade (Cotidiano) | 🔴 Defasada | 🔴 Defasada | Não (rodada 3 tentou, revertida — voltou ao estado original) |

**3 de 11 âncoras subiram de categoria** (Corporativo e `__tecnico__` com salto de 2 níveis,
Solenidade com 1 nível). **8 de 11 não mudaram** — 3 delas (Vitalidade, Noturno, Sublime) já eram
saudáveis e continuam; 5 (Conexão, Conflito, Distanciamento, Nostalgia, Simplicidade) permanecem com
os mesmos problemas documentados no diagnóstico original, seja por não terem sido alvo de nenhuma
rodada (Distanciamento, Nostalgia), seja porque as tentativas de correção foram revertidas por causa
de regressões (Conexão parcialmente, Conflito, Simplicidade).

## Estado do repositório

Inalterado nesta tarefa. 54 frases / 11 âncoras, o mesmo estado deixado ao final da rodada 5.
