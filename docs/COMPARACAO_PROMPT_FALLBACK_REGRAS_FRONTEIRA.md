# Comparação: prompt de fallback antigo vs. novo (regras de fronteira) — validado com Mistral real

Compara o fallback semântico (`call_semantic_fallback`, thresholds `score_min=0.63`/`gap_min=0.04`
documentados em `CALIBRACAO_THRESHOLD_MISTRAL.md`) nos mesmos **46 casos** (Grupo A + B) usados em
`IMPLEMENTACAO_FALLBACK_MISTRAL.md`, trocando só o conteúdo de `prompts/fallback.md`: a versão antiga
listava as 10 âncoras com descrição curta, sem regras de fronteira; a nova adiciona regra de
fronteira por âncora (ex. "rosto pequeno numa multidão é Conflito, não Conexão") e um campo
`reasoning` no JSON de resposta, além de uma saída `"AMBIGUO"` explícita pra casos que não se
encaixam com confiança.

**20 chamadas reais ao Mistral** (`ministral-14b-latest`, via litellm), mesmos 46 casos, 48.3s
totais. Nenhuma âncora ou threshold foi alterado.


## Resultado agregado

| | Acurácia | Casos corretos | Resgatados dos 12 difíceis | Regressões nos 34 fáceis |
|---|---|---|---|---|
| SBERT-only (baseline, sem fallback) | 73.9% | 34/46 | — | — |
| **Prompt antigo** (real, doc anterior) | 78.3% | 36/46 | 2/12 (25% quando chamado) | 0/34 |
| **Prompt novo** (real, este teste) | **87.0%** | **40/46** | **7/12 (87.5% quando chamado)** | **1/34** |

Disparo do fallback: **20/46 chamadas em ambos os testes** (8 dos 12 difíceis + 12 dos 34 fáceis) —
idêntico ao prompt antigo, como esperado, já que o gatilho é score/gap do SBERT e nenhuma âncora ou
threshold mudou. A diferença inteira vem de o Mistral decidir melhor uma vez chamado.

## Os 12 casos difíceis — quem o Mistral resgatou

| Caso | Esperado | Prompt antigo | Prompt novo |
|---|---|---|---|
| `sobrecarga sensorial, nada no lugar` | Conflito | ✅ Conflito | ✅ Conflito |
| `grão de filme genuíno em retrato quase preto e branco` | Nostalgia | ✅ Nostalgia | ✅ Nostalgia |
| `pessoa em roupa profissional mas em ambiente real, não estúdio` | Simplicidade | ❌ manteve Corporativo | ✅ **Simplicidade (novo)** |
| `multidão animada mas com clima positivo, sem tensão` | Vitalidade | ❌ manteve Noturno | ✅ **Vitalidade (novo)** |
| `rosto pequeno e dividido em meio a uma multidão` | Conflito | ❌ foi pra Distanciamento | ✅ **Conflito (novo)** |
| `atleta com expressão de dor extrema no rosto` | Conflito | ❌ manteve Vitalidade | ✅ **Conflito (novo)** |
| `pessoa lendo sem posar` | Simplicidade | ❌ foi pra Conexão | ✅ **Simplicidade (novo)** |
| `estética vintage só que digitalmente perfeita, sem grão real` | Ambíguo/descarte | ❌ manteve Nostalgia | ❌ manteve Nostalgia (ver nota) |
| `pessoa sozinha ao entardecer, sombras longas` | (não deveria ser Distanciamento) | Não disparou (score 0.725) | Não disparou (score 0.725) |
| `retrato próximo e emotivo em ambiente de estúdio formal` | Conexão | Não disparou (score 0.706) | Não disparou (score 0.706) |
| `show de rock em ambiente escuro` | Noturno | Não disparou (score 0.657) | Não disparou (score 0.657) |
| `produto isolado em fundo branco` | Solenidade | Colide com `__tecnico__`, não entra na branch | Colide com `__tecnico__`, não entra na branch |

**5 dos 6 casos que o prompt antigo errava por não ter a regra certa agora são resolvidos** — cada um
bate exatamente com uma regra de fronteira nova (dor física → Conflito não Vitalidade; rosto pequeno
em multidão → Conflito não Conexão; roupa formal em ambiente real → Simplicidade não Corporativo;
multidão animada sem contexto de festa → Vitalidade não Noturno). Os 4 que continuam sem resgate são
os mesmos 3 "confiante e errado" já documentados como teto estrutural do score/gap (não chegam a
chamar o Mistral) mais a colisão pré-existente com `__tecnico__` — nenhum dos dois é resolvível só
ajustando o prompt.

### `reasoning` reportado pelo Mistral nos casos resgatados

- **roupa profissional em ambiente real** → Simplicidade: *"roupa profissional em um ambiente real e
  não controlado (...) exclui âncoras como Corporativo (...) A cena é cotidiana e não produzida"*
- **multidão animada sem tensão** → Vitalidade: *"energia e movimento genuíno, mas sem contexto
  explícito de festa ou celebração (...) A vibe central é a ação e energia coletiva"*
- **rosto pequeno em multidão** → Conflito: *"caracteriza tensão e sobrecarga sensorial, não
  intimidade ou proximidade emocional (...) apenas caos e dispersão"*
- **atleta com dor extrema** → Conflito: *"exclui Vitalidade (que exige ação genuína sem dor) e se
  enquadra claramente na definição de Conflito"*
- **pessoa lendo sem posar** → Simplicidade: *"cena parece real e não produzida, com foco no
  cotidiano"*

Em todos os 5, o `reasoning` cita literalmente a regra de fronteira nova (não só a âncora certa por
acaso) — evidência de que o Mistral está de fato usando o conhecimento adicionado, não acertando por
outro motivo.

### Nota sobre `"estética vintage... sem grão real"` (não resolvido de forma estável)

Na chamada oficial dos 46 casos, o Mistral manteve `Nostalgia` (mesmo erro do prompt antigo). Numa
chamada isolada de reprodução (mesmo prompt, mesmo texto, `temperature=0.1`), o Mistral respondeu
`"AMBIGUO"` com reasoning *"estética vintage digitalmente perfeita, sem grão ou textura analógica
genuína, o que invalida a âncora Nostalgia (...) não se encaixa em nenhuma outra categoria com
clareza"* — ou seja, **a instrução funciona, mas não de forma determinística**: `temperature=0.1` não
é zero, e esse caso especificamente fica na fronteira de decisão do próprio modelo. Não é uma falha do
prompt (a regra e o reasoning corretos aparecem quando ele acerta), é variância de amostragem.
`_resolve_anchor_label` já trata `"AMBIGUO"`/`"AMBÍGUO"` corretamente (nenhuma âncora tem esse nome,
então cai no fallback gracioso pro top1 do SBERT — que, coincidentemente, já era `Nostalgia` nesse
caso, então o resultado final não muda mesmo quando o Mistral responde `AMBIGUO`).

## Os 34 casos que já eram corretos — a única regressão

| Caso | Esperado | Score/gap SBERT | Prompt antigo | Prompt novo |
|---|---|---|---|---|
| `olhos fechados, luz de contorno, mão tocando o queixo` | Conexão | dispara fallback | ✅ manteve Conexão | ❌ **flipou pra Solenidade** |

`reasoning` do Mistral nesse caso: *"luz de contorno (iluminação controlada e estilizada) e uma pose
deliberada (...) indica uma produção fotográfica intencional e estática (...) o foco não é um
close-up emocional genuíno"*. A nova regra de Solenidade ("cobre cenas visivelmente encenadas mesmo
fora de contexto de estúdio tradicional") capturou esse caso por engano — a cena tem produção
deliberada (luz de contorno) **e** proximidade emocional (mão no queixo, olhos fechados), e o Mistral
pesou o primeiro sinal mais que o segundo. É o único caso, de 12 disparos desnecessários, em que a
regra nova confundiu uma resposta que já estava certa — os outros 11 se mantiveram corretos.

**A regra de Distanciamento×Sublime especificamente não confundiu nenhum caso** — os 3 casos de
paisagem/escuridão do corpus (`montanha grandiosa fotografada à noite`, `paisagem grandiosa mas
fotografada no escuro`, `pessoa sozinha ao entardecer`) mantiveram o resultado esperado nos dois
prompts.

## Veredito

| | Prompt antigo | Prompt novo |
|---|---|---|
| Acurácia real | 78.3% (36/46) | **87.0% (40/46)** |
| Resgates | 2/12 | 7/12 |
| Regressões | 0/34 | 1/34 |
| Saldo líquido vs. antigo | — | **+4 casos corretos** |

O prompt novo entrega um ganho real líquido de +4 casos (as 5 correções líquidas dos difíceis, menos
1 regressão nos fáceis) sobre os já modestos +2 do prompt antigo — e o `reasoning` confirma que o
ganho vem das regras de fronteira, não de acaso. A única regressão (Conexão→Solenidade) e a
inconsistência do caso "vintage digital" são o preço de dar ao modelo regras mais específicas: elas
ajudam mais do que atrapalham (5:1 nesse corpus), mas não são infalíveis. Nenhuma mudança de
arquitetura foi feita — grau de resgate/regressão é inteiramente efeito do texto do prompt.

## Arquivos gerados

- `data/processed/fallback_live_validation.json` — os 46 casos completos desta rodada (mesmo formato
  de antes, sobrescrito pela nova rodada real)
- `data/processed/fallback_live_validation_reasoning.json` — `reasoning` bruto do Mistral pros 8
  casos que mudaram de resultado (7 resgates + 1 regressão), capturado à parte porque
  `validate_fallback_live.py` não persiste a resposta bruta do fallback semântico

## Estado do repositório

**Aplicado.** `prompts/fallback.md` já está com o conteúdo novo (regras de fronteira + `reasoning` +
`AMBIGUO`). `_parse_json_object`/`_resolve_anchor_label` não precisaram de mudança — o campo
`reasoning` extra é ignorado automaticamente, e `"AMBIGUO"` cai no fallback gracioso existente sem
código novo. `litellm_adapter.py` corrigido (não injeta mais prompt duplicado). `settings.py` ganhou
defaults em código pros campos novos (`LLM_MODEL_CURRENT_NAME=mistral/ministral-14b-latest`,
`LLM_MODEL_CURRENT_TEMPERATURE=0.1`, DeepSeek/Claude keys vazias) sem exigir edição do `.env`.
