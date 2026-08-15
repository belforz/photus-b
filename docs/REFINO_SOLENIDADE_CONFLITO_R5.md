# Reforço de Solenidade e Conflito — Rodada 5 (Passo 4/5/6/7)

Continuação de `DIAGNOSTICO_PRE_R5.md` (só diagnóstico) e da série de rodadas 1-4. Escopo: 3 frases
afirmativas novas — 1 em Solenidade, 2 em Conflito. `THRESHOLD_TECNICO`, `CONFIDENCE_THRESHOLD_LOW`,
Simplicidade, Conexão, Corporativo, `__tecnico__` e as demais âncoras não foram tocados.

**Resultado: critério parcialmente atingido. 1 das 3 frases causou uma regressão real fora do
escopo mapeado (Grupo A de Noturno) e foi isolada/revertida; as outras 2 ficaram.**

## O que foi feito

1. **Backup** (Passo 1): confirmado estado de partida = pós-rodada-4 (52 frases: Solenidade 4,
   Simplicidade 4, Conflito 4, Conexão 4, Corporativo 5, `__tecnico__` 9). Backup em
   `data/processed/anchor_backups/solenidade_before_r5.json`, `conflito_before_r5.json`,
   `knowledge_anchors_before_r5.json`.
2. **3 frases novas adicionadas** (Passo 2):
   - Solenidade (+1): *"cena claramente produzida e estilizada, composição encenada com intenção
     estética evidente, resultado de produção fotográfica cuidadosa e deliberada"*
   - Conflito (+2): *"rosto pequeno e distante em meio a uma multidão grande e apertada, apenas mais
     uma pessoa perdida no meio de tantas outras"* e *"cada elemento fora do lugar, cena bagunçada e
     caótica, objetos espalhados ao acaso por toda a superfície"*
3. Script: `scripts/anchors/compare_r5.py`, com breakdown por frase individual nos 3 casos-alvo.

## Rodada inicial (3 frases juntas) — resultado misto

| Caso-alvo | Esperado | Antes | Depois (3 frases) |
|---|---|---|---|
| `cena doméstica mas visivelmente produzida e estilizada` | Solenidade | Simplicidade 0.620 | **Solenidade 0.700 ✅** |
| `rosto pequeno e disperso em meio a uma multidão` | Conflito | Conexão 0.596 | **Conflito 0.895 ✅** (dominante) |
| `sobrecarga sensorial, nada no lugar` | Conflito | Solenidade 0.557 | Solenidade 0.557 ❌ (sem mudança) |

2 dos 3 casos-alvo foram corrigidos, incluindo um resultado muito forte (0.895) no caso do
"rosto numa multidão". Mas o Grupo A completo (30 casos) encontrou uma regressão real:

| Caso (Grupo A) | Esperado | Antes | Depois (3 frases) |
|---|---|---|---|
| `show com multidão eufórica` | **Noturno (Festa)** | Noturno 0.584 | **Conflito 0.630 ❌** |

**Este caso não estava no escopo mapeado** (nenhuma das 4 âncoras do diagnóstico pré-r5 é Noturno) —
achado só possível pela checagem ampla do Grupo A completo, exatamente como o Passo 5 pediu.

### Isolando o driver (breakdown por frase)

| Score | Frase | Âncora |
|---|---|---|
| **0.630** | `rosto pequeno e distante em meio a uma multidão grande e apertada...` (nova) | Conflito |
| 0.584 | `foto de festa, balada, celebração, evento social à noite` | Noturno |
| 0.569 | `amigos juntos, dança, euforia, animado, desinibido, multidão feliz` | Noturno |

A frase nova 1 de Conflito (a que resolveu o caso-alvo "rosto numa multidão") é inequivocamente a
driver — sobreposição lexical de "multidão" entre a frase nova e o caso de Noturno, o mesmo padrão
de risco já visto nas rodadas 3/4 (frase forte demais em torno de um substantivo comum).

## Ação: isolar e reverter só a frase problemática (Passo 6)

Conforme instruído, **não revertidas as 3 juntas.** Removida só a frase 1 de Conflito ("rosto
pequeno e distante..."). Mantidas: a frase de Solenidade e a frase 2 de Conflito ("cada elemento
fora do lugar..."). Embeddings regenerados. `data/raw/knowledge_anchors.json` ficou em **54 frases**
(52 + 2, não +3).

### Resultado após isolar (estado final aplicado)

| Caso-alvo | Esperado | Resultado final |
|---|---|---|
| `cena doméstica mas visivelmente produzida e estilizada` | Solenidade | **✅ Solenidade 0.700 — mantido** |
| `rosto pequeno e disperso em meio a uma multidão` | Conflito | **❌ Conexão 0.596 — voltou a falhar** (a frase que resolvia foi a mesma que causou a regressão; não há como manter uma sem a outra com esta formulação) |
| `sobrecarga sensorial, nada no lugar` | Conflito | ❌ Solenidade 0.557 — sem mudança (frase 2 sozinha não é forte o suficiente: 0.454 vs. 0.557) |
| `show com multidão eufórica` (Grupo A, Noturno) | Noturno | **✅ Noturno 0.584 — regressão desfeita** |

## Checagem de regressão completa, estado final (Passo 5)

- **Grupo A completo (30 casos):** **30/30 idênticos** — zero divergência, confirmando que isolar a
  frase problemática resolveu a regressão sem introduzir nenhuma outra.
- **Casos de guarda:** 3 aparecem como "errados" (`pessoa lendo sem posar` → Distanciamento 0.394;
  `produto isolado em fundo branco` → `__tecnico__` 0.511; `olhos fechados, luz de contorno...` →
  Distanciamento 0.521), mas os 3 têm **score idêntico antes e depois**, em ambas as versões
  testadas (3 frases e versão isolada) — são limitações pré-existentes, não relacionadas a esta
  rodada (mesmo padrão de falso-alarme já documentado na rodada 3).
- **Checagem cruzada rodadas 1-4:** os 3 casos (`retrato de estúdio emotivo`, `coquetel corporativo`,
  `executivo sorrindo`) e os 3 casos centrais de Corporativo permanecem intactos, sem mudança de
  score.
- **Corpus técnico (9 casos):** 9/9 idênticos, `__tecnico__` intacto.

## Critério de parada (Passo 6) — por frase

| Frase | Causou regressão? | Resolveu o alvo? | Decisão |
|---|---|---|---|
| Solenidade: "cena claramente produzida..." | Não | Sim (0.700) | **Mantida** |
| Conflito: "rosto pequeno e distante... multidão" | **Sim** (Noturno → Conflito) | Sim (0.895) | **Revertida** |
| Conflito: "cada elemento fora do lugar..." | Não | Não (0.454 < 0.557) | **Mantida** (inócua, não resolveu mas não piora nada) |

**Critério geral: parcialmente atingido.** 1 de 3 casos-alvo permanece corrigido (Solenidade), 2 de 3
permanecem como limitação (o de Conflito/Conexão voltou a falhar depois de reverter a única frase
capaz de resolvê-lo; o de Conflito/Solenidade nunca chegou a ser resolvido). Zero regressão no estado
final.

## Estado atual do repositório

**Aplicado, parcialmente.** `data/raw/knowledge_anchors.json` tem 54 frases (Solenidade 5, Conflito
5 — só a frase de "sobrecarga sensorial" ficou, a de "rosto numa multidão" foi revertida).
`src/scripts/anchors/sbert_json.py` reflete esse estado. Backup do estado com as 3 frases (antes de
isolar) não foi salvo separadamente — só o backup pré-rodada-5 (`knowledge_anchors_before_r5.json`,
52 frases) e o texto exato da frase revertida ficam documentados aqui, caso se queira reconstruir.

## Pendências / limitações conhecidas atualizadas

- `"roupa profissional mas em ambiente real, não estúdio"` — já fechado como limitação conhecida na
  rodada 4 (ver `REFINO_CONEXAO_R4.md`), sem mudança nesta rodada.
- `"rosto pequeno e disperso em meio a uma multidão"` (esperado Conflito, cai em Conexão 0.596) —
  **novo caso fechado como limitação conhecida.** A única frase testada capaz de resolvê-lo
  ("rosto pequeno e distante... multidão grande e apertada") compartilha vocabulário de "multidão"
  forte o suficiente pra vazar pro Grupo A de Noturno (`"show com multidão eufórica"`). Uma frase
  mais específica (ex.: evitando repetir "multidão" como termo central, ou reduzindo o quanto a
  frase pesa em "grande e apertada") poderia funcionar, mas não foi tentada nesta rodada — fica pra
  uma eventual rodada 6, se quiser.
- `"sobrecarga sensorial, nada no lugar"` (Grupo A do próprio Conflito, cai em Solenidade 0.557) —
  permanece sem solução. A frase testada ("cada elemento fora do lugar...") chegou a 0.454, mais
  perto do que os 0.405 originais mas ainda 0.10 abaixo do necessário. Fica registrado como
  pendência em aberto (não como limitação fechada, já que só uma tentativa foi feita e não causou
  nenhum efeito colateral — uma 2ª variação dessa frase específica ainda é uma opção razoável, ao
  contrário dos casos de Corporativo/Simplicidade e Conflito/Conexão, que já esgotaram 2 abordagens
  estruturalmente diferentes cada).
