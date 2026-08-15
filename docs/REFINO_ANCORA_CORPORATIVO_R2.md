# Refino da âncora Corporativo (Focado) — Rodada 2 (Passo 4/5/6)

Continuação de `REFINO_ANCORA_CORPORATIVO.md` (rodada 1). Escopo: reescrever só a frase 3 de
Corporativo, mantendo as outras 4 intactas. `THRESHOLD_TECNICO`, `CONFIDENCE_THRESHOLD_LOW` e as
outras âncoras não foram tocados.

## O que foi feito

1. **Backup** (Passo 1): `data/processed/anchor_backups/corporativo_before_r2.json` (5 frases +
   embeddings, estado pós-rodada-1) e snapshot completo
   `data/processed/anchor_backups/knowledge_anchors_before_corporativo_r2.json`.
2. **Frase 3 reescrita** (Passo 2), mantendo as outras 4 intactas:
   - antes: *"imagem de executivo, chefe, funcionário, empresário, headshot, foto de perfil
     profissional"*
   - depois: *"headshot corporativo formal em estúdio ou fundo controlado, foto de perfil
     profissional para uso oficial, pose séria e composta, sem ambiente doméstico e sem expressão
     espontânea"*
   Embeddings regenerados (só essa frase). `data/raw/knowledge_anchors.json` continua com 51 frases.
   **Mudança já está live.**
3. Script: `scripts/anchors/compare_corporativo_r2.py`.

## Resultado — a hipótese de causa raiz não se confirmou

## Tabela comparativa (Passo 4) — casos-alvo desta rodada

| Caso | Esperado | Top1/Score antes | Top1/Score depois |
|---|---|---|---|
| `roupa profissional mas em ambiente real, não estúdio` | Simplicidade | Corporativo 0.617 | **Corporativo 0.649** (piorou) |
| `sessão de fotos de estúdio com o executivo sorrindo..., clima descontraído` | Conexão / zona cinzenta | Corporativo 0.722 | Corporativo 0.583 (melhorou, mas continua erro confiante ≥ 0.45) |

**Nenhum dos 2 casos-alvo passou no critério** (nem bateu na âncora certa, nem deixou de ser erro
confiante). Um piorou, o outro melhorou mas não o suficiente.

### Por que piorou: negação não funciona bem em embeddings de frase

Investigando os scores por frase individual (não só o máximo por âncora), a frase 3 nova virou a
frase de **maior score** para `"roupa profissional mas em ambiente real, não estúdio"` — 0.649,
acima de todas as outras 4 frases de Corporativo:

| Score | Frase de Corporativo |
|---|---|
| **0.649** | `headshot corporativo formal em estúdio ou fundo controlado... **sem ambiente doméstico** e sem expressão espontânea` (nova) |
| 0.617 | pose formal e distante para estúdio... (rodada 1) |
| 0.480 | foto profissional para currículo, linkedin... (original) |

A cláusula de exclusão explícita ("sem ambiente doméstico", "sem expressão espontânea") **não
empurrou o embedding pra longe** do caso de teste — pelo contrário, a frase nova é mais densa em
vocabulário de "ambiente"/"profissional"/"estúdio" do que a frase antiga que substituiu, e modelos
de sentence-embedding com mean pooling não tratam negação de forma confiável: a presença lexical de
"ambiente doméstico" no texto da âncora conta a favor da similaridade, independente do "sem" na
frente. O mesmo padrão apareceu no caso de generalização
`"empresário posando para revista, ambiente de escritório real, sem produção de estúdio"`
(esperado Simplicidade/zona cinzenta): a frase nova também virou a top-1 driver, com score subindo
de 0.478 para 0.610.

Achado a registrar: **frases de âncora com negação/exclusão ("sem X", "não Y") não são uma
estratégia confiável nessa pipeline** — o efeito observado nas duas rodadas de refino até agora foi
sempre o oposto do esperado quando a frase menciona o conceito que deveria excluir.

## Checagem de regressão (Passo 5)

- **Grupo A completo (30 casos):** 28/30 idênticos. As 2 divergências são, de novo, dentro do
  próprio Corporativo — e desta vez são melhoras claras, não pioras: `headshot com fundo neutro de
  estúdio` subiu de 0.547 para **0.647** e `iluminação de estúdio limpa, roupa formal` de 0.552 para
  0.555 (ambos já corretos antes e depois). **Zero divergência fora de Corporativo.**
- **3 casos centrais de Corporativo:** nenhum piorou (os 3 continuam corretos; 2 melhoraram de
  score).
- **2 casos-alvo da rodada 1:** continuam batendo sem mudança (`retrato de estúdio emotivo` → Conexão
  0.715; `cena social mas estática e formal, tipo coquetel corporativo` → Corporativo 0.655).
- **Corpus técnico (9 casos):** 9/9 idênticos, `__tecnico__` intacto.

## Critério de parada (Passo 6)

| Critério | Resultado |
|---|---|
| 2 casos-alvo da rodada 2 corrigidos (ou sem erro confiante) | ❌ **FALHOU** (nenhum dos 2) |
| 3 casos centrais de Corporativo não pioraram vs. pós-rodada-1 | ✅ OK (melhoraram) |
| 2 casos-alvo da rodada 1 continuam batendo | ✅ OK |
| `__tecnico__` sem efeito colateral | ✅ OK |
| Grupo A completo sem divergência fora de Corporativo | ✅ OK (0/27) |

**Critério geral: NÃO atingido.** A rewrite piorou um dos dois casos-alvo (0.617→0.649) e só
melhorou parcialmente o outro (0.722→0.583, ainda erro confiante). Não tentei corrigir sozinho —
reportando os números e a causa raiz (negação não funciona nessa pipeline) pra você decidir.

## Estado atual do repositório

**Revertido.** A rewrite da frase 3 foi desfeita: `data/raw/knowledge_anchors.json` e
`src/scripts/anchors/sbert_json.py` foram restaurados a partir de
`data/processed/anchor_backups/knowledge_anchors_before_corporativo_r2.json` e
`sbert_json_before_corporativo_r2.py.bak` — de volta ao estado pós-rodada-1 (5 frases, frase 3
original "imagem de executivo, chefe, funcionário, empresário, headshot, foto de perfil
profissional"). O critério da rodada 1 continua valendo; as 2 pendências abaixo seguem em aberto
pra uma eventual rodada 3, sem frases de negação/exclusão.

## Pendências que continuam em aberto

- `"roupa profissional mas em ambiente real, não estúdio"` → esperado Simplicidade, cai em
  Corporativo (piorou nesta rodada: 0.617→0.649 com a rewrite; se reverter, volta a 0.617).
- `"sessão de fotos de estúdio com o executivo sorrindo..., clima descontraído"` → esperado Conexão/
  zona cinzenta, cai em Corporativo (melhorou nesta rodada: 0.722→0.583; se reverter, volta a 0.722).
