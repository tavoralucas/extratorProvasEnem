import pdfplumber
import re
import pandas as pd
import logging

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Abre o arquivo PDF
pdf_path = "/Users/tavoralucas/Desktop/extratorProvasEnem/gabarito/enem24gabaritoProva2dia.pdf"
logger.info(f"Tentando abrir o arquivo PDF: {pdf_path}")

all_text = ""
try:
    with pdfplumber.open(pdf_path) as pdf:
        logger.info(f"PDF aberto com sucesso. Número de páginas: {len(pdf.pages)}")
        for i, page in enumerate(pdf.pages, 1):
            page_text = page.extract_text()
            if page_text:
                logger.info(f"Texto extraído da página {i}: {len(page_text)} caracteres")
                all_text += page_text + "\n"
            else:
                logger.warning(f"Nenhum texto encontrado na página {i}")
except Exception as e:
    logger.error(f"Erro ao abrir o PDF: {str(e)}")
    raise

logger.info(f"Total de texto extraído: {len(all_text)} caracteres")

# Lista para armazenar os dados do gabarito
gabarito_data = []

# Processa as questões de Matemática (136-180)
for i in range(136, 181):
    padrao = re.compile(f"{i}\s+([A-E])")
    match = padrao.search(all_text)
    if match:
        resposta = match.group(1)
        gabarito_data.append({
            "numero": i,
            "area": "Matematica e suas Tecnologias",
            "resposta": resposta
        })
    else:
        logger.warning(f"Não foi possível encontrar a resposta para a questão {i}")

logger.info(f"Total de respostas processadas: {len(gabarito_data)}")

# Conversão para DataFrame
df = pd.DataFrame(gabarito_data)
logger.info(f"DataFrame criado com {len(df)} linhas e {len(df.columns)} colunas")

# Salvando o DataFrame em um arquivo JSON
output_filename = "enem_extracao_gabarito_matematica.json"
df.to_json(output_filename, orient='records', indent=4)
logger.info(f"Arquivo '{output_filename}' gerado com sucesso!")
