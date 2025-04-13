
# Extração Estruturada de Questões do ENEM

## Objetivo
Este projeto tem como objetivo realizar a extração automatizada e organizada de todas as questões das provas do Exame Nacional do Ensino Médio (**ENEM**) disponibilizadas em formato **PDF**, convertendo-as para um formato estruturado (**XLSX**), permitindo sua utilização em sistemas educacionais e bancos de dados.

## Justificativa
As questões do **ENEM** são um recurso valioso para a análise de desempenho estudantil, criação de simulados e desenvolvimento de conteúdos educacionais adaptativos. A extração manual dessas questões é demorada, sujeita a erros e pouco escalável. Este sistema automatizado resolve esses problemas, garantindo eficiência, consistência e escalabilidade.

## Escopo e Estrutura
Cada questão extraída segue rigorosamente esta estrutura:

* **Número:** Sequencial (1 a 90).
* **Idioma:** Inglês ou espanhol para questões 1 a 5; único para as demais.
* **Área:** Linguagens (questões 1-45); Ciências (questões 46-90).
* **Título:** Caso exista.
* **Texto de Apoio:** Contextualização que antecede o enunciado.
* **Imagem:** Indica presença ou ausência (True/False).
* **Fonte:** Informações de fonte presentes explicitamente na questão.
* **Enunciado:** Pergunta principal.
* **Alternativas (A-E):** Textos das alternativas oferecidas.
* **Gabarito:** Alternativa correta indicada no final da prova.

## Ferramentas e Tecnologias
* **Python:** Para automação e processamento.
* **pdfplumber** ou **PyMuPDF:** Para extração de texto e imagens de **PDFs**.
* **pandas:** Estruturação dos dados e exportação em **XLSX**.
* **Regex:** Identificação e segmentação dos blocos das questões.

## Resultados Esperados
* Arquivo **XLSX** estruturado com todas as questões organizadas.
* Automação que reduz significativamente erros humanos e o tempo necessário para a tarefa.
* Escalabilidade para processar diferentes provas e anos do **ENEM**.

## Aplicações Futuras
O arquivo estruturado será utilizado como base de dados para aplicações educacionais, tais como simulados adaptativos, análises detalhadas de conteúdos e estudos estatísticos sobre as questões do **ENEM**.