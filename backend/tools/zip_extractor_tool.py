from crewai.tools import tool
import os
import shutil
import sys

# Adiciona o diretório tools ao path para importar functions
sys.path.insert(0, os.path.dirname(__file__))
from functions import descompactar_arquivo

@tool("zip_extractor")
def zip_extractor_tool(caminho_arquivo_zip: str) -> str:
    """
    Extrai arquivos ZIP, 7Z, RAR, ARJ para o diretório dados/notasfiscais.
    Esta ferramenta usa a função descompactar_arquivo do functions.py
    e é especializada em descompactar arquivos contendo dados fiscais.
    
    Args:
        caminho_arquivo_zip: Caminho completo para o arquivo compactado
    
    Returns:
        Mensagem de sucesso ou erro com detalhes da extração
    """
    try:
        # Verifica se o arquivo existe
        if not os.path.exists(caminho_arquivo_zip):
            return f"❌ Erro: Arquivo não encontrado em {caminho_arquivo_zip}"
        
        # Define o diretório de destino baseado no arquivo ZIP
        # Se o arquivo está em uploads/, extrai para uploads/dados/notasfiscais
        destino = os.path.join(os.path.dirname(caminho_arquivo_zip), 'dados', 'notasfiscais')
        
        # Cria o diretório de destino se não existir
        os.makedirs(destino, exist_ok=True)
        
        # Limpa o diretório de destino
        for arquivo in os.listdir(destino):
            caminho_arquivo = os.path.join(destino, arquivo)
            try:
                if os.path.isfile(caminho_arquivo):
                    os.unlink(caminho_arquivo)
                elif os.path.isdir(caminho_arquivo):
                    shutil.rmtree(caminho_arquivo)
            except Exception as e:
                print(f"⚠️ Aviso: Não foi possível limpar {caminho_arquivo}: {e}")
        
        # Usa a função descompactar_arquivo do functions.py
        print(f"🔄 Iniciando extração de {caminho_arquivo_zip} para {destino}")
        descompactar_arquivo(caminho_arquivo_zip, destino)
        
        # Verifica os arquivos extraídos
        arquivos_extraidos = os.listdir(destino)
        csv_files = [f for f in arquivos_extraidos if f.lower().endswith('.csv')]
        
        if not csv_files:
            return f"⚠️ Aviso: Nenhum arquivo CSV encontrado após extração em {destino}"
        
        # Procura especificamente pelos arquivos esperados
        cabecalho_file = None
        itens_file = None
        
        for arquivo in csv_files:
            nome_lower = arquivo.lower()
            if 'cabecalho' in nome_lower or 'header' in nome_lower:
                cabecalho_file = arquivo
            elif 'itens' in nome_lower or 'items' in nome_lower:
                itens_file = arquivo
        
        # Monta o relatório de resultado
        resultado = f"✅ Extração concluída com sucesso usando functions.py!\n"
        resultado += f"📂 Destino: {destino}\n"
        resultado += f"📄 Arquivos extraídos: {len(arquivos_extraidos)}\n"
        resultado += f"📊 CSVs encontrados: {len(csv_files)}\n"
        
        if cabecalho_file:
            resultado += f"🗂️ Arquivo de cabeçalhos: {cabecalho_file}\n"
        if itens_file:
            resultado += f"📋 Arquivo de itens: {itens_file}\n"
        
        if not cabecalho_file or not itens_file:
            resultado += f"⚠️ Aviso: Não foram encontrados os arquivos padrão '*cabecalho*.csv' e '*itens*.csv'\n"
        
        resultado += f"📋 CSVs disponíveis: {', '.join(csv_files)}\n"
        resultado += f"🎯 Base de dados RAG atualizada e pronta para consultas!"
        
        return resultado
        
    except FileNotFoundError as e:
        return f"❌ Erro: {str(e)}"
    except PermissionError:
        return f"❌ Erro: Permissão negada para acessar {caminho_arquivo_zip} ou diretório de destino"
    except Exception as e:
        return f"❌ Erro inesperado durante a extração: {str(e)}"