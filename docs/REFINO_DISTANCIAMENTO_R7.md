# Refino de Distanciamento (Low-key) — Rodada 7

Continuação de `DIAGNOSTICO_PRE_R7_DISTANCIAMENTO.md` e da série de rodadas 1-6. Escopo: reescrever
as 4 frases existentes (todas listas de palavras soltas) em prosa + 1 frase nova contra o vazamento
documentado pra Sublime. `THRESHOLD_TECNICO`, `CONFIDENCE_THRESHOLD_LOW` e todas as outras âncoras
não foram tocados.

**Resultado: critério atingido — os 2 problemas-alvo foram resolvidos, score médio subiu, zero
regressão real (nenhum caso correto virou errado em nenhum lugar do sistema).** Mudança aplicada e
mantida.

## O que foi feito

1. **Backup**: `data/processed/anchor_backups/distanciamento_before_r7.json` (4 frases + embeddings,
   estado pós-rodada-6) e snapshot completo `knowledge_anchors_before_r7.json` (54 frases).
2. **4 frases reescritas + 1 nova** (Distanciamento vai de 4 para 5 frases):
   - `"foto escura, sombria e pesada"` → *"cena dominada pela escuridão, ambiente sombrio e pesado,
     iluminação baixa e dura de propósito"*
   - `"lugar vazio, abandonado, desolado, concreto"` → *"lugar vazio e abandonado, estrutura de
     concreto desolada, sem nenhum sinal de vida ao redor"*
   - `"solitário, isolado, triste, frio, melancólico, silencioso, distante"` → *"sensação de
     isolamento profundo e silêncio pesado, uma tristeza fria, melancólica e distante"*
   - `"sensação de solidão, ninguém por perto, ambiente opressivo, luz baixa e dura"` → *"sensação de
     solidão total, ninguém por perto, muitas vezes apenas um ponto de luz pequeno e intenso —
     poste, janela ou lâmpada isolada — destacado contra uma escuridão vasta e dominante"*
   - **(nova)** *"paisagem ou cenário grandioso fotografado completamente às escuras, a escala
     impressionante do lugar apagada pela falta de luz"*
   `data/raw/knowledge_anchors.json` foi de 54 para **55 frases**. **Mudança aplicada e ativa.**
3. Script: `scripts/anchors/compare_r7.py`, com breakdown por frase nos 2 casos-alvo.

## Grupo A de Distanciamento — score médio subiu de 0.666 para 0.706, acerto foi de 2/3 para 3/3

| Caso | Esperado | Antes | Depois |
|---|---|---|---|
| `poste de luz solitário contra escuridão quase total` | Distanciamento | **Vitalidade 0.725 (errado)** | **Distanciamento 0.834 (correto) ✅** |
| `corredor vazio e escuro` | Distanciamento | Distanciamento 0.614 (correto) | Distanciamento 0.640 (correto, +0.026) |
| `silhueta isolada, ninguém por perto` | Distanciamento | Distanciamento 0.658 (correto) | Distanciamento 0.643 (correto, -0.015) |

**Os 3 casos centrais agora são todos corretos** — o miss identificado no diagnóstico pré-rodada foi
resolvido.

## Os 2 problemas-alvo — breakdown por frase, resolvidos com folga

### Problema 1: `"poste de luz solitário contra escuridão quase total"` (era Vitalidade 0.725)

| Score | Frase | Âncora |
|---|---|---|
| **0.834** | `cena dominada pela escuridão, ambiente sombrio e pesado, iluminação baixa e dura de propósito` (reescrita) | Distanciamento |
| 0.816 | `sensação de solidão total, ninguém por perto, muitas vezes apenas um ponto de luz pequeno e intenso — poste, janela ou lâmpada isolada — destacado contra uma escuridão vasta e dominante` (reescrita) | Distanciamento |
| 0.746 | `paisagem ou cenário grandioso fotografado completamente às escuras...` (nova) | Distanciamento |
| 0.725 | `foto clara, branca, superexposta... sem sombra` (a que vencia antes) | Vitalidade |

A reescrita da frase 4 (mencionando explicitamente "poste, janela ou lâmpada isolada" contra
escuridão) atacou exatamente o padrão de antônimo-por-palavra-"luz" identificado no diagnóstico —
agora vence com folga (0.834 vs. 0.725, gap de 0.109 a favor da âncora certa, contra os 0.028 de
antes a favor da âncora errada).

### Problema 2: `"paisagem grandiosa mas fotografada no escuro"` (era Sublime 0.842)

| Score | Frase | Âncora |
|---|---|---|
| **0.903** | `paisagem ou cenário grandioso fotografado completamente às escuras, a escala impressionante do lugar apagada pela falta de luz` (nova) | Distanciamento |
| 0.842 | `foto de paisagem enorme e impressionante` (a que vencia antes) | Sublime |

A frase nova, desenhada especificamente pra esse padrão ("grandioso" + "escuras"), venceu com folga
(0.903 vs. 0.842).

## Grupo B — casos de fronteira

| Caso | Esperado | Antes | Depois |
|---|---|---|---|
| `paisagem grandiosa mas fotografada no escuro` | Distanciamento | Sublime 0.842 (TRAP) | **Distanciamento 0.903 (HIT) ✅** |
| `pessoa sozinha ao entardecer, sombras longas` | (nenhuma — não deveria ser Distanciamento) | Distanciamento 0.702 | Distanciamento 0.725 (+0.023, levemente mais confiante na armadilha — não era alvo desta rodada) |
| `montanha grandiosa fotografada à noite` | Sublime | Sublime 0.755 | Sublime 0.755 (sem mudança) |
| `ambiente escuro mas festivo e animado` | Noturno | Noturno 0.705 | Noturno 0.705 (sem mudança) |
| `show de rock em ambiente escuro` | Noturno | Distanciamento 0.600 (errante) | Distanciamento 0.657 (errante, sem mudar de âncora) |

**Nota sobre o caso de observação:** `"pessoa sozinha ao entardecer, sombras longas"` — como avisado
no escopo, não era alvo desta rodada, e o score subiu levemente (0.702→0.725). É um efeito colateral
esperado: a frase reescrita 4 (que agora cobre melhor "luz baixa e dura" com uma cena de
poste/lâmpada isolada) também generalizou um pouco pra qualquer cena de luz fraca/sombras, incluindo
esta que deveria ser rejeitada. O aumento é pequeno (+0.023) e o caso já era uma armadilha confirmada
antes — não é uma regressão nova, mas fica registrado como leve piora a observar numa eventual rodada
futura dedicada a esse caso específico.

## Casos de guarda (Vitalidade e Sublime, Grupo A) — zero vazamento

Os 6 casos de guarda (3 de Vitalidade, 3 de Sublime) têm **score idêntico antes e depois**, ao
milésimo. As frases novas de Distanciamento não vazaram para nenhum dos dois vizinhos de risco
mapeados no diagnóstico.

## Checagem de regressão completa

- **Casos-alvo das rodadas 1-6** (5 casos): todos com score idêntico, sem mudança.
- **Grupo A completo (30 casos):** 24/30 idênticos. As 6 divergências, detalhadas:
  - 3 são os próprios ganhos de Distanciamento (documentados acima).
  - `"olhos fechados, luz de contorno, mão tocando o queixo"` (Conexão) — **melhora bônus**: antes
    ia erroneamente para Distanciamento (0.521, já era um caso pré-existente mal roteado, não
    causado por esta sessão), agora vai corretamente para Conexão (0.510).
  - `"pessoa lendo sem posar"` (Simplicidade) — continua errado (Distanciamento), score
    praticamente idêntico (0.394→0.391). Sem mudança de status.
  - `"grão de filme genuíno em retrato quase preto e branco"` (Nostalgia) — já era um miss
    pré-existente (ia pra Distanciamento, 0.651, não documentado antes). Continua errado, mas agora
    vai para Solenidade (0.622) em vez de Distanciamento — troca de âncora errada por outra âncora
    errada, não é uma regressão nova (não havia nada "correto" pra regredir aqui).

  **Nenhuma dessas 6 divergências é uma regressão real** (nenhum caso que estava correto passou a
  estar errado) — 3 são o ganho pretendido, 1 é uma correção bônus, e 2 são realocações entre
  âncoras já erradas antes e depois.
- **Corpus técnico (9 casos):** 8/9 idênticos. `"deixa o assunto nítido e o fundo totalmente
  desfocado"` teve o `top1_anchor` mudar de Distanciamento (0.418) pra `__tecnico__` (0.390), mas
  `technical_score` e a decisão `technical=False` são **idênticos** antes e depois — mudança
  puramente cosmética no rótulo informativo do top1, sem efeito funcional no roteamento.

## Critério de parada

| Critério | Resultado |
|---|---|
| Problema 1 (poste de luz vs. Vitalidade) resolvido | ✅ OK (0.834 vs. 0.725, gap de 0.109 a favor) |
| Problema 2 (paisagem grandiosa escura vs. Sublime) resolvido | ✅ OK (0.903 vs. 0.842) |
| Score médio de Distanciamento sobe | ✅ OK (0.666 → 0.706) |
| Casos de guarda (Vitalidade, Sublime) sem vazamento | ✅ OK (0/6, score idêntico) |
| Casos-alvo das rodadas 1-6 intactos | ✅ OK |
| Grupo A completo sem regressão real (correto→errado) | ✅ OK (as 6 divergências são ganho, bônus, ou realocação entre erros pré-existentes) |
| Corpus técnico sem efeito funcional | ✅ OK (`technical`/`technical_score` idênticos) |

**Critério geral: ATINGIDO.** Não foi necessário isolar nenhuma das 5 frases.

## Estado atual do repositório

**Aplicado.** `data/raw/knowledge_anchors.json` tem 55 frases (Distanciamento com 5, todas em
prosa — nenhuma é mais lista de palavras soltas). `src/scripts/anchors/sbert_json.py` reflete essa
mudança.

## Pendência registrada (fora de escopo desta rodada)

`"pessoa sozinha ao entardecer, sombras longas"` continua caindo em Distanciamento quando não
deveria, e piorou ligeiramente (0.702→0.725) como efeito colateral não-alvo desta rodada. Fica
registrado para uma eventual rodada dedicada a esse caso específico, que exigiria uma frase que
distinga "luz fraca/sombras de fim de tarde" (não deveria ativar Distanciamento) de "escuridão
opressiva" (deveria) — nenhuma tentativa foi feita ainda.

## Atualização da classificação de saúde

Distanciamento (Low-key) estava classificada 🟠 Defasada desde o diagnóstico original. Com os 3
casos centrais do Grupo A agora corretos (era 2/3) e os 2 problemas de fronteira documentados
resolvidos, a classificação sobe para **🟡 Saudável com ressalva** — mesmo patamar de Vitalidade e
Noturno: central forte, mas ainda com uma ressalva de fronteira conhecida e não endereçada
(`"pessoa sozinha ao entardecer"`).
