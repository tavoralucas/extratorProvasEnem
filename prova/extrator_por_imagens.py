import pytesseract
from PIL import Image
import json
import re
import os
import glob

# --- Configuração ---
# Se o Tesseract não estiver no PATH do sistema, descomente e ajuste a linha abaixo:
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe' # Exemplo para Windows
# pytesseract.pytesseract.tesseract_cmd = r'/usr/local/bin/tesseract' # Exemplo para macOS/Linux

image_path = '/Users/tavoralucas/Desktop/extratorProvasEnem/prova/questoes_matematica/'  # Caminho para a pasta de imagens
output_json_file = '/Users/tavoralucas/Desktop/extratorProvasEnem/prova/questoes_extraidas_matematica.json'
language_ocr = 'por'  # Define o idioma para o OCR (Português)
# --- Fim da Configuração ---

def limpar_texto(texto):
    """
    Limpa o texto extraído do OCR, removendo caracteres especiais e normalizando espaços.
    """
    # Substitui caracteres especiais
    texto = texto.replace('|', 'I')  # Corrige engenheiro | para engenheiro I
    texto = texto.replace('Il', 'II')  # Corrige engenheiro Il para engenheiro II
    texto = texto.replace('Ill', 'III')  # Corrige engenheiro Ill para engenheiro III
    texto = texto.replace('€', '')  # Remove o símbolo do euro
    texto = texto.replace('&', '')  # Remove o &
    texto = texto.replace('UESTÃ', 'QUESTÃO')  # Corrige UESTÃ para QUESTÃO
    texto = re.sub(r'QUESTÃO+O*', 'QUESTÃO', texto)  # Remove Os extras após QUESTÃO
    texto = re.sub(r'O\s+([A-E][\.\)])', r'\1', texto)  # Remove O antes das alternativas
    texto = re.sub(r'OQ', '', texto)  # Remove OQ solto
    
    # Remove múltiplos espaços
    texto = re.sub(r'\s+', ' ', texto)
    
    # Remove quebras de linha extras
    texto = texto.replace('\n', ' ').strip()
    
    # Corrige valores monetários
    texto = re.sub(r'R\$\s*(\d+)\s*[,\.]\s*(\d+)', r'R$ \1,\2', texto)  # Formato R$ X,XX
    texto = re.sub(r'(\d+)\s*[,\.]\s*(\d+)', r'\1,\2', texto)  # Formato X,XX
    
    # Corrige números com caracteres 'I' no meio
    texto = re.sub(r'(\d+)\s*I\s*(\d+)', r'\1\2', texto)
    
    # Remove espaços entre números e vírgulas em valores monetários
    texto = re.sub(r'(\d+)\s+(\d+),(\d+)', r'\1\2,\3', texto)
    
    # Remove espaços extras antes e depois de vírgulas
    texto = re.sub(r'\s*,\s*', ', ', texto)
    
    # Corrige valores monetários sem vírgula
    texto = re.sub(r'(\d+)\s+00', r'\1,00', texto)
    
    return texto.strip()

def extrair_informacoes_questao(caminho_imagem, idioma='por'):
    """
    Extrai informações da imagem principal da questão.

    Args:
        caminho_imagem (str): O caminho para o arquivo de imagem.
        idioma (str): O código do idioma para o Tesseract OCR.

    Returns:
        dict: Um dicionário com as informações extraídas ou None se falhar.
    """
    try:
        # Abre a imagem
        img = Image.open(caminho_imagem)
        texto_extraido = pytesseract.image_to_string(img, lang=idioma)
        texto_limpo = limpar_texto(texto_extraido)
        
        # Extrai o número da questão do nome do arquivo
        numero_questao = re.search(r'questao_(\d+)', os.path.basename(caminho_imagem)).group(1)
        
        return {
            'numero': numero_questao,
            'texto_principal': texto_limpo
        }
    except Exception as e:
        print(f"Erro ao processar imagem principal: {e}")
        return None

def extrair_informacoes_alternativas(caminho_imagem, idioma='por'):
    """
    Extrai enunciado e alternativas da imagem de alternativas.

    Args:
        caminho_imagem (str): O caminho para o arquivo de imagem.
        idioma (str): O código do idioma para o Tesseract OCR.

    Returns:
        dict: Um dicionário com enunciado e alternativas ou None se falhar.
    """
    try:
        img = Image.open(caminho_imagem)
        texto_extraido = pytesseract.image_to_string(img, lang=idioma)
        texto_limpo = limpar_texto(texto_extraido)
        
        # Encontra as alternativas usando valores numéricos
        alternativas = {}
        valores = re.findall(r'(\d+,\d+|\d+)', texto_limpo)
        valores = [v for v in valores if len(v) >= 4]  # Filtra apenas valores com 4 ou mais dígitos
        
        # Associa os valores às letras A, B, C, D, E
        letras = ['A', 'B', 'C', 'D', 'E']
        for i, valor in enumerate(valores[:5]):  # Limita a 5 alternativas
            # Formata o valor com vírgula e zeros se necessário
            if ',' not in valor:
                valor = f"{valor},00"
            alternativas[letras[i]] = valor
        
        # Remove os valores das alternativas e textos desnecessários do enunciado
        enunciado = texto_limpo
        for valor in valores:
            enunciado = enunciado.replace(valor, '')
        
        # Remove textos desnecessários do enunciado
        enunciado = re.sub(r'[A-E]\s*[\)\.]\s*', '', enunciado)  # Remove letras das alternativas
        enunciado = re.sub(r'\s*,\s*00\s*\.?', '', enunciado)  # Remove ",00" soltos
        enunciado = re.sub(r'O\s+', '', enunciado)  # Remove O solto
        enunciado = re.sub(r'\s+', ' ', enunciado).strip()  # Normaliza espaços
        
        return {
            'enunciado': enunciado,
            'alternativas': alternativas
        }
    except Exception as e:
        print(f"Erro ao processar alternativas: {e}")
        return None

def salvar_em_json(dados, nome_arquivo):
    """
    Salva os dados extraídos em um arquivo JSON.

    Args:
        dados (list): Uma lista de dicionários, onde cada dicionário contém
                      as informações de uma questão ('numero', 'enunciado', 'alternativas').
        nome_arquivo (str): O nome do arquivo JSON de saída.
    """
    if not dados:
        print("Nenhum dado para salvar no JSON.")
        return

    try:
        # Se o arquivo já existe, carrega os dados existentes
        dados_existentes = []
        if os.path.exists(nome_arquivo):
            with open(nome_arquivo, 'r', encoding='utf-8') as f:
                dados_existentes = json.load(f)
        
        # Remove questões duplicadas (mesma numeração)
        numeros_existentes = set()
        dados_unicos = []
        
        # Primeiro, adiciona os dados novos
        for questao in dados:
            numero = questao.get('numero')
            if numero not in numeros_existentes:
                numeros_existentes.add(numero)
                dados_unicos.append(questao)
        
        # Depois, adiciona os dados existentes que não têm número duplicado
        for questao in dados_existentes:
            numero = questao.get('numero')
            if numero not in numeros_existentes:
                numeros_existentes.add(numero)
                dados_unicos.append(questao)
        
        # Salva os dados únicos no arquivo JSON
        with open(nome_arquivo, 'w', encoding='utf-8') as f:
            json.dump(dados_unicos, f, ensure_ascii=False, indent=4)
        
        print(f"Dados salvos com sucesso em '{nome_arquivo}'")

    except PermissionError:
        print(f"Erro: Permissão negada para salvar o arquivo '{nome_arquivo}'. Verifique se ele não está aberto em outro programa.")
    except Exception as e:
        print(f"Ocorreu um erro ao salvar o arquivo JSON: {e}")

def processar_todas_questoes(caminho_pasta, idioma='por'):
    """
    Processa todas as imagens de questões na pasta especificada.

    Args:
        caminho_pasta (str): Caminho para a pasta contendo as imagens das questões.
        idioma (str): O código do idioma para o Tesseract OCR.

    Returns:
        list: Lista de dicionários contendo as informações extraídas de todas as questões.
    """
    todas_questoes = []
    
    # Lista apenas as pastas que contêm arquivos
    pastas_com_conteudo = verificar_pastas_com_conteudo(caminho_pasta)
    
    for pasta_num in pastas_com_conteudo:
        try:
            numero_questao = int(pasta_num)
            pasta_questao = os.path.join(caminho_pasta, pasta_num)
            
            # Procura por todos os tipos de arquivos da questão
            arquivo_questao = glob.glob(os.path.join(pasta_questao, f"questao_{numero_questao}.*"))[0]
            arquivo_alternativas = glob.glob(os.path.join(pasta_questao, f"enunciado_alternativas_{numero_questao}.*"))[0]
            arquivo_acessorio = glob.glob(os.path.join(pasta_questao, f"imagem_acessorio_{numero_questao}.*"))[0] if glob.glob(os.path.join(pasta_questao, f"imagem_acessorio_{numero_questao}.*")) else None
            
            print(f"Processando questão {numero_questao}")
            
            # Processa cada parte da questão
            info_questao = extrair_informacoes_questao(arquivo_questao, idioma)
            info_alternativas = extrair_informacoes_alternativas(arquivo_alternativas, idioma)
            
            if info_questao and info_alternativas:
                questao_completa = {
                    'numero': numero_questao,
                    'texto_principal': info_questao['texto_principal'],
                    'enunciado': info_alternativas['enunciado'],
                    'alternativas': info_alternativas['alternativas']
                }
                
                # Adiciona o caminho da imagem acessória se existir
                if arquivo_acessorio:
                    questao_completa['imagem_acessorio'] = arquivo_acessorio
                
                todas_questoes.append(questao_completa)
                print(f"✓ Questão {numero_questao} processada com sucesso")
            
        except Exception as e:
            print(f"✗ Erro ao processar questão {pasta_num}: {e}")
            continue
    
    return todas_questoes

def verificar_pastas_com_conteudo(caminho_pasta):
    """
    Verifica quais pastas contêm arquivos e retorna uma lista das pastas não vazias.

    Args:
        caminho_pasta (str): Caminho para a pasta principal contendo as subpastas de questões.

    Returns:
        list: Lista de pastas que contêm arquivos.
    """
    pastas_com_conteudo = []
    
    # Lista todas as pastas de questões
    pastas_questoes = [d for d in os.listdir(caminho_pasta) if os.path.isdir(os.path.join(caminho_pasta, d))]
    
    for pasta_num in pastas_questoes:
        try:
            pasta_questao = os.path.join(caminho_pasta, pasta_num)
            # Lista arquivos na pasta
            arquivos = [f for f in os.listdir(pasta_questao) if os.path.isfile(os.path.join(pasta_questao, f))]
            
            # Se a pasta contém arquivos, adiciona à lista
            if arquivos:
                pastas_com_conteudo.append(pasta_num)
                
        except Exception as e:
            print(f"Erro ao verificar pasta {pasta_num}: {e}")
            continue
    
    return sorted(pastas_com_conteudo, key=lambda x: int(x))

# --- Execução Principal ---
if __name__ == "__main__":
    if not os.path.exists(image_path):
        print(f"Erro Crítico: A pasta '{image_path}' não foi encontrada.")
        print("Verifique o valor da variável 'image_path' no código.")
    else:
        # Verifica quais pastas contêm arquivos
        pastas_com_conteudo = verificar_pastas_com_conteudo(image_path)
        
        if not pastas_com_conteudo:
            print("Nenhuma pasta com arquivos foi encontrada.")
            print("Certifique-se de que existem imagens nas pastas das questões.")
        else:
            print(f"Encontradas {len(pastas_com_conteudo)} pastas com arquivos:")
            for pasta in pastas_com_conteudo:
                print(f"- Pasta {pasta}")
            
            print("\nIniciando processamento das questões...")
            # Processa todas as questões na pasta
            todas_questoes = processar_todas_questoes(image_path, language_ocr)
            
            if todas_questoes:
                # Salva todas as questões no arquivo JSON
                salvar_em_json(todas_questoes, output_json_file)
                print(f"\nTotal de questões processadas com sucesso: {len(todas_questoes)}")
            else:
                print("\nNão foi possível extrair dados de nenhuma imagem.")