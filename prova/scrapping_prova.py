import pdfplumber
import re
import pandas as pd
import os

def extrair_questoes_pdf(caminho_pdf):
    """
    Extrai blocos de texto correspondentes a questões de um arquivo PDF.
    Assume que cada questão começa com "QUESTÃO" seguido de um número.
    """
    questoes_extraidas = []
    if not os.path.exists(caminho_pdf):
        print(f"Erro: Arquivo PDF não encontrado em '{caminho_pdf}'")
        return questoes_extraidas

    try:
        with pdfplumber.open(caminho_pdf) as pdf:
            texto_completo = ""
            print(f"Lendo PDF: {caminho_pdf} ({len(pdf.pages)} páginas)")

            # Extrair texto de todas as páginas (ignorando a primeira)
            for num_pagina, page in enumerate(pdf.pages[1:], start=2):
                try:
                    texto_pagina = page.extract_text()
                    if texto_pagina:
                        texto_completo += texto_pagina + "\n"
                    else:
                        print(f"Aviso: Nenhum texto extraído da página {num_pagina}")
                except Exception as e_page:
                    print(f"Erro ao extrair texto da página {num_pagina}: {e_page}")

            if not texto_completo.strip():
                print("Erro: O texto extraído do PDF está vazio.")
                return questoes_extraidas

            # Padrão para encontrar o início das questões
            padrao_inicio_questao = r'(^\s*QUESTÃO\s+\d+)'
            partes = re.split(padrao_inicio_questao, texto_completo, flags=re.MULTILINE)

            if len(partes) > 1:
                for i in range(1, len(partes), 2):
                    marcador = partes[i]
                    texto_questao = partes[i+1] if i + 1 < len(partes) else ""
                    questao_completa = (marcador + texto_questao).strip()
                    
                    # Extrai o número da questão
                    num_match = re.search(r'QUESTÃO\s+(\d+)', marcador)
                    if num_match:
                        num_questao = int(num_match.group(1))
                        # Adiciona apenas se for questão 136 ou superior
                        if num_questao >= 136:
                            questoes_extraidas.append(questao_completa)

    except Exception as e:
        print(f"Ocorreu um erro inesperado ao processar o PDF: {e}")

    return questoes_extraidas

def extrair_alternativas(texto):
    """
    Extrai as alternativas (A a E) de um bloco de texto de questão.
    """
    alt_dict = {"A": "", "B": "", "C": "", "D": "", "E": ""}
    alt_pattern = re.compile(r"\n([A-E])\s+(.*?)(?=\n[A-E]\s+|\Z)", re.DOTALL)
    matches = re.findall(alt_pattern, texto)
    for letra, conteudo in matches:
        alt_dict[letra] = conteudo.strip()
    return alt_dict

def processar_questoes(questoes, df_gabarito):
    """
    Processa a lista de questões extraídas e retorna um DataFrame estruturado.
    """
    questions_data = []
    gabaritos = dict(zip(df_gabarito['numero'], df_gabarito['resposta']))

    for questao in questoes:
        # Extrai o número da questão
        num_match = re.search(r'QUESTÃO\s+(\d+)', questao)
        if not num_match:
            continue
        
        num = int(num_match.group(1))
        
        # Extrai o enunciado (tudo até a primeira alternativa)
        partes = questao.split("\nA ")
        enunciado = partes[0].strip()
        
        # Extrai as alternativas
        alternativas = extrair_alternativas(questao)
        
        # Verifica se há imagens
        imagem_presente = "Figura" in questao or "Imagem" in questao
        
        # Obtém o gabarito
        gabarito = gabaritos.get(num, "")
        
        questions_data.append({
            "numero": num,
            "enunciado": enunciado,
            "imagem": imagem_presente,
            "alternativa_a": alternativas["A"],
            "alternativa_b": alternativas["B"],
            "alternativa_c": alternativas["C"],
            "alternativa_d": alternativas["D"],
            "alternativa_e": alternativas["E"],
            "alternativa_correta": gabarito
        })

    return pd.DataFrame(questions_data)

def main():
    # Caminhos dos arquivos
    pdf_path = "/Users/tavoralucas/Desktop/extratorProvasEnem/prova/2024_PV_impresso_D2_CD5.pdf"
    gabarito_path = os.path.join("gabarito", "enem_extracao_gabarito_matematica.xlsx")

    # Lê o arquivo de gabarito
    df_gabarito = pd.read_excel(gabarito_path)
    print("Colunas disponíveis no arquivo de gabarito:", df_gabarito.columns.tolist())

    # Extrai as questões do PDF (apenas a partir da 136)
    questoes = extrair_questoes_pdf(pdf_path)
    print(f"\n--- {len(questoes)} QUESTÕES DE MATEMÁTICA EXTRAÍDAS ---")

    # Processa as questões e gera o DataFrame final
    df = processar_questoes(questoes, df_gabarito)

    # Reordena as colunas
    colunas = [
        "numero",
        "enunciado",
        "imagem",
        "alternativa_a",
        "alternativa_b",
        "alternativa_c",
        "alternativa_d",
        "alternativa_e",
        "alternativa_correta"
    ]
    df = df[colunas]

    # Salva o resultado na pasta prova
    output_filename = os.path.join("prova", "banco_questoes_matematica.xlsx")
    df.to_excel(output_filename, index=False)
    print(f"Arquivo '{output_filename}' gerado com sucesso!")

if __name__ == "__main__":
    main()
