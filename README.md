# Photus B

[![License](https://img.shields.io/badge/license-MIT-blue)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.8+-blue)](https://www.python.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-4.x-blue)](https://www.typescriptlang.org/)
[![uv](https://img.shields.io/badge/uv-Package%20Manager-green)](https://github.com/astral-sh/uv)

O **Photus B** é um processador de linguagem natural, originado de técnicas avançadas de classificação semântica na resolução de inferências propostas pelo usuário, visando complementar o direcionamento das melhores e mais adequadas fotos. O uso de um grande modelo de linguagem da família Mistral é usado somente para inferências que não obtiveram uma resposta satisfatório pelo próprio processador, visando fallback ou conclusões de JSON proveniente do Photus A. Este projeto integra técnicas avançadas de classificação semântica para analisar e interpretar consultas em linguagem natural, com o objetivo de identificar e linkar fotos processadas pelo Photus A, devolvendo ao usuário exatamente aquilo que foi solicitado em inferências.

## Sobre o Photus A

O Photus A é um modelo de avaliação de qualidade de imagens baseado em aprendizado de máquina, desenvolvido em C++ com OpenCV e Python. O Photus B complementa essa funcionalidade ao processar consultas naturais e conectar os resultados de avaliação de imagens a respostas contextuais.

## Técnicas de Classificação Semântica

O Photus B emprega técnicas de classificação semântica, incluindo:
- Análise de embeddings semânticos para compreensão contextual.
- Modelos de linguagem multimodal para integração de texto e imagens.
- Algoritmos de fallback usando Magistrall da família Mistral, aplicados somente para inferências que o Photus B não conseguir alcançar, garantindo robustez em inferências incertas.
- Conclusão de JSON estruturado baseado em dados do Photus A.

## Objetivo

O principal objetivo do Photus B é identificar e linkar as fotos apuradas pelo Photus A, permitindo devolver ao usuário o conteúdo solicitado por meio de inferências em linguagem natural. Isso facilita a interação intuitiva com bancos de imagens processadas.

## Tecnologias

- **Python**: Linguagem principal para processamento de linguagem natural e integração com Magistrall.
- **uv**: Gerenciador de pacotes rápido e eficiente para Python.
- **TypeScript**: Utilizado em partes menores para interfaces ou scripts auxiliares, proporcionando tipagem estática onde necessário.

## Licença

Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

Copyright (c) 2025 Leo

## Contribuição

1. Faça um fork do repositório
2. Crie uma branch de funcionalidade
3. Faça suas alterações
4. Adicione testes se aplicável
5. Envie um pull request

## Suporte

Para problemas ou dúvidas, abra uma issue no repositório GitHub.
*
---

*Feito com ❤️ para processamento inteligente de linguagem natural e imagens.*
