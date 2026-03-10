### 1. O Mapa de Âncoras (Eixos Polares e Tradução Física)

Para evitar o "borrão semântico" no modelo de linguagem (SBERT/Bertimbau), as 15 âncoras não operam como conceitos isolados, mas como **antônimos em eixos de tensão**. Além disso, o motor traduz a abstração poética para a física visual, permitindo que a Visão Computacional encontre o conceito.

As 15 âncoras formam o espaço latente distribuídas nestes eixos principais:

*   **Eixo da Energia (Ação vs. Estase):**
    *   *Vitalidade / Espontaneidade:* Cores vibrantes, alto contraste, assimetria, leve *motion blur*, alta energia.
    *   *Solenidade / Serenidade:* Simetria rígida, entropia baixíssima (fundo limpo), iluminação suave e equilibrada, cores neutras.

*   **Eixo da Abertura (Conexão vs. Isolamento):**
    *   *Conexão / Vulnerabilidade:* Rosto em evidência, iluminação frontal clara, alta nitidez no sujeito, olhar direto.
    *   *Distanciamento / Introspecção:* Rosto ocupando pouca área, sombras duras (*low-key*), alto *dynamic range*, olhar desviado ou silhuetas.

*   **Eixo da Tensão (Leveza vs. Gravidade):**
    *   *Simplicidade / Cotidianidade:* Iluminação natural, saturação média, baixo contraste, cenários ordinários.
    *   *Conflito / Complexidade:* Cenários caóticos (alta entropia), iluminação dramática (claro-escuro marcado), múltiplas texturas.

*   **Eixo do Tempo e Narrativa:**
    *   *Nostalgia:* Cores desbotadas (baixa saturação), texturas suaves/ruído, luz quente de fim de tarde, baixo contraste (estética analógica).
    *   *Sublime / Intensidade:* Escala grandiosa (rosto mínimo perante o cenário), saturação intensa, exposição perfeita, alto impacto visual.
    *   *Narratividade:* Elementos contextuais fortes no cenário, profundidade de campo média (cenário legível junto com o sujeito).

*(Teste de Sanidade: Antes de ir para produção, o sistema gera uma Matriz de Colisão entre as descrições das âncoras. Se a Similaridade de Cosseno entre duas âncoras for $&gt; 0.65$, seus textos de "bula" devem ser reescritos com vocabulário mais distante).*

### 2. Extração Automática do "Eu" (100% Photus A / Visão Computacional)

O "Eu" atua como um multiplicador de força ($W_{eu}$) baseado estritamente na gramática visual real extraída pelas matrizes do Photus A:

*   **Intimidade (Distância/Foco):** Calculada pela métrica `face.areaRatio` somada à razão de Bokeh (`face.sharpness` / `edgeDensityValue` global). Rosto grande com fundo matematicamente borrado eleva o peso para Conexão e Vulnerabilidade ($1.5x$). Planos abertos onde tudo está em foco reduzem o multiplicador e puxam para Distanciamento ou Paisagem ($0.7x$).
*   **Empatia (Ângulo 3D):** Utiliza-se a detecção de *landmarks* faciais cruzada com algoritmos de pose estimation (ex: `solvePnP` do OpenCV) para extrair o *Pitch, Yaw e Roll* da cabeça. Câmera no nível dos olhos ($\pm 10^\circ$) valida Verdade e Sinceridade. Ângulos extremos identificados na geometria do rosto (Picado/Contrapicado) deslocam o score para Fragilidade ou Poder.
*   **Intencionalidade (Composição):** O rigor geométrico (medido pelo baixo `centerOffset` e bordas alinhadas) pontua em Solenidade; o desequilíbrio estrutural e detecção de *motion blur* pontuam em Espontaneidade.

### 3. O Cálculo do Score Final e Ranquemanto Dinâmico

O Photus B decompõe o prompt do usuário, encontra a interpolação exata no espaço latente e aplica a projeção escalar contra as métricas devolvidas pelo Photus A:

$$Score = (\text{Vetor}_{\text{Sentimento}} \cdot \text{Vetor}_{\text{Imagem}}) \times W_{\text{eu}}$$

*   **O Limite Dinâmico (Threshold):** Devido à natureza dos Sentence Transformers (onde a dispersão matemática varia conforme o conceito), o uso de um corte fixo (ex: $&lt; 0.7$) foi abolido. O sistema passa a usar **Ranqueamento Relativo**. Apenas o Top 10% a 15% das fotos com os maiores Scores daquela galeria são promovidas como "Sugestões Fortes". Resultados abaixo da média da própria amostra são descartados como "ruído semântico" ou falha de *match*.

---

### 4. Análise Visual da Matriz de Colisão

A imagem `anchors_firstversion.png` apresenta a **Matriz de Colisão das Âncoras**, que é a implementação visual do "Teste de Sanidade". Esta matriz utiliza um mapa de calor (*heatmap*) para exibir a similaridade de cosseno entre os vetores de cada âncora. A escala de cores vai de azul (baixa similaridade, valor próximo de 0.0) a vermelho (alta similaridade, valor próximo de 1.0).

O objetivo é garantir que cada âncora seja semanticamente distinta o suficiente para não gerar ambiguidade no modelo.

**Interpretação da Matriz:**

1.  **Validação do "Teste de Sanidade":** O critério definido é que uma similaridade maior que **0.65** (cor laranja-avermelhada intensa) indicaria uma colisão, exigindo a reescrita das descrições das âncoras. Ao analisar a matriz, observamos que os valores mais altos são:
    *   `Vitalidade (Ação)` vs. `Noturno (Festa)`: **0.62**
    *   `Nostalgia (Analógico)` vs. `Noturno (Festa)`: **0.62**
    *   `Distanciamento (Low-key)` vs. `Noturno (Festa)`: **0.61**

    Como nenhum par de âncoras distintas ultrapassa o limiar de 0.65, **o conjunto de âncoras passa no teste de sanidade**. Isso confirma que, para o modelo, os conceitos são suficientemente separados.

2.  **Separação e Contraste Semântico:** A matriz também revela os pares de âncoras que o modelo considera mais distantes (cores mais frias/azuladas), validando os eixos de tensão conceituais:
    *   `Solenidade (Estase)` vs. `Conflito (Caos)`: **0.13** (azul escuro). Este é o par com menor similaridade, confirmando que o modelo os vê como conceitos quase opostos, alinhados com o **Eixo da Energia**.
    *   `Solenidade (Estase)` vs. `Sublime (Paisagem)`: **0.23**.
    *   `Conflito (Caos)` vs. `Conexão (Close-up)`: **0.21**.

Em resumo, a matriz de colisão não apenas valida a arquitetura de âncoras (passando no teste de sanidade), mas também fornece um mapa visual claro de como o modelo de linguagem agrupa e diferencia os conceitos fotográficos, garantindo a precisão do motor de busca.
