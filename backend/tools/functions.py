import zipfile
import subprocess
import os
import pandas as pd
from pydantic import BaseModel

class NFs_Cabecalho(BaseModel):
    # Defina os campos de acordo com o cabeçalho do arquivo '202401_NFs_Cabecalho.csv'
    pass

class NFs_Itens(BaseModel):
    # Defina os campos de acordo com o cabeçalho do arquivo '202401_NFs_Itens.csv'
    pass

def descompactar_arquivo(caminho_arquivo: str, diretorio_destino: str) -> None:
    pasta_temporaria = diretorio_destino
    os.makedirs(pasta_temporaria, exist_ok=True)

    if not os.path.isfile(caminho_arquivo):
     raise FileNotFoundError(f"Arquivo {caminho_arquivo} não encontrado.")

    extensao = caminho_arquivo.lower().split('.')[-1]
    os.chdir(pasta_temporaria)

    if extensao == 'zip':
        try:
            with zipfile.ZipFile(caminho_arquivo, 'r') as zip_ref:
                zip_ref.extractall()
            print(f"Arquivo {caminho_arquivo} descompactado com sucesso em {diretorio_destino}.")
        except Exception as e:
            print(f"Erro ao descompactar {caminho_arquivo}: {e}")

    elif extensao == 'arj':
        try:
            subprocess.run(['arj', 'x', caminho_arquivo], check=True)
            print(f"Arquivo {caminho_arquivo} descompactado com sucesso em {diretorio_destino}.")
        except subprocess.CalledProcessError as e:
            print(f"Erro ao descompactar {caminho_arquivo}: {e}")

    elif extensao == '7z':
        try:
            subprocess.run(['7z', 'x', caminho_arquivo], check=True)
            print(f"Arquivo {caminho_arquivo} descompactado com sucesso em {diretorio_destino}.")
        except subprocess.CalledProcessError as e:
            print(f"Erro ao descompactar {caminho_arquivo}: {e}")

    elif extensao in ['tar', 'gz', 'tgz']:
        try:
            comando = ['tar', '-xvf' if extensao == 'tar' else '-xzvf', caminho_arquivo]
            subprocess.run(comando, check=True)
            print(f"Arquivo {caminho_arquivo} descompactado com sucesso em {diretorio_destino}.")
        except subprocess.CalledProcessError as e:
            print(f"Erro ao descompactar {caminho_arquivo}: {e}")

    elif extensao == 'iso':
        try:
            subprocess.run(['7z', 'x', caminho_arquivo], check=True)
            print(f"Arquivo {caminho_arquivo} descompactado com sucesso em {diretorio_destino}.")
        except subprocess.CalledProcessError as e:
            print(f"Erro ao descompactar {caminho_arquivo}: {e}")

    else:
        print(f"Formato de arquivo {caminho_arquivo} não suportado.")

def ler_e_estruturar_dados(caminho_arquivos):
    arquivos_csv = [f for f in os.listdir(caminho_arquivos) if f.endswith('.csv')]
    dados_estruturados = {}

    for arquivo in arquivos_csv:
        caminho_arquivo = os.path.join(caminho_arquivos, arquivo)
        try:
            df = pd.read_csv(caminho_arquivo, sep=',', decimal='.')
            if 'NFs_Cabecalho' in arquivo:
                dados_estruturados['NFs_Cabecalho'] = [
                    NFs_Cabecalho(**row) for row in df.to_dict(orient='records')
                ]
            elif 'NFs_Itens' in arquivo:
                dados_estruturados['NFs_Itens'] = [
                    NFs_Itens(**row) for row in df.to_dict(orient='records')
                ]
            else:
                print(f"Arquivo {arquivo} não reconhecido.")
        except Exception as e:
            print(f"Erro ao processar {arquivo}: {e}")

    return dados_estruturados
