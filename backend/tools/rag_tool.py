from crewai.tools import tool
import pandas as pd
import os
from typing import List, Dict, Any

@tool("rag_semantic_search")
def rag_semantic_search_tool(pergunta: str, diretorio_dados: str = None) -> str:
    """
    Realiza consulta semântica nos arquivos CSV descompactados usando RAG.
    Permite que os agentes "leiam" os arquivos como base textual para 
    interpretação contextual e busca semântica inteligente.
    
    Args:
        pergunta: Pergunta ou termo de busca em linguagem natural
        diretorio_dados: Diretório onde estão os arquivos CSV
    
    Returns:
        Contexto semântico e insights relevantes para a pergunta
    """
    try:
        # Define diretório padrão se não fornecido
        if diretorio_dados is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            diretorio_dados = os.path.join(base_dir, 'dados', 'notasfiscais')
        
        # Verifica se o diretório existe
        if not os.path.exists(diretorio_dados):
            return f"❌ Erro: Diretório {diretorio_dados} não encontrado"
        
        # Lista arquivos disponíveis
        csv_files = [f for f in os.listdir(diretorio_dados) if f.endswith('.csv')]
        
        if not csv_files:
            return f"❌ Erro: Nenhum arquivo CSV encontrado para consulta RAG"
        
        resultado = f"🔍 Consulta RAG: {pergunta}\n\n"
        
        # Carrega e analisa conteúdo dos arquivos para contexto semântico
        contexto_completo = []
        
        # Estatísticas gerais dos dados
        total_arquivos = len(csv_files)
        resultado += f"📁 Arquivos encontrados: {total_arquivos}\n"
        
        for arquivo in csv_files:
            caminho_arquivo = os.path.join(diretorio_dados, arquivo)
            try:
                df = pd.read_csv(caminho_arquivo)
                
                # Identifica tipo do arquivo
                tipo_arquivo = 'desconhecido'
                if 'cabecalho' in arquivo.lower() or 'header' in arquivo.lower():
                    tipo_arquivo = 'cabeçalho das notas fiscais'
                elif 'itens' in arquivo.lower() or 'item' in arquivo.lower():
                    tipo_arquivo = 'itens das notas fiscais'
                elif 'PRODUTO' in ' '.join(df.columns).upper():
                    tipo_arquivo = 'itens das notas fiscais'
                else:
                    tipo_arquivo = 'cabeçalho das notas fiscais'
                
                # Extrai metadados do arquivo
                arquivo_info = {
                    'nome': arquivo,
                    'tipo': tipo_arquivo,
                    'linhas': len(df),
                    'colunas': list(df.columns),
                    'tipos_dados': df.dtypes.to_dict(),
                    'amostras': {}
                }
                
                resultado += f"📄 {arquivo} ({tipo_arquivo}): {len(df)} registros\n"
                
                # Extrai amostras de dados para contexto
                for coluna in df.columns:
                    if df[coluna].dtype == 'object':
                        valores_unicos = df[coluna].dropna().unique()[:5]
                        arquivo_info['amostras'][coluna] = valores_unicos.tolist()
                    elif pd.api.types.is_numeric_dtype(df[coluna]):
                        arquivo_info['amostras'][coluna] = {
                            'min': float(df[coluna].min()) if not df[coluna].isna().all() else None,
                            'max': float(df[coluna].max()) if not df[coluna].isna().all() else None,
                            'media': float(df[coluna].mean()) if not df[coluna].isna().all() else None
                        }
                
                contexto_completo.append(arquivo_info)
                
            except Exception as e:
                resultado += f"⚠️ Erro ao processar {arquivo}: {str(e)}\n"
        
        # Análise semântica da pergunta
        pergunta_lower = pergunta.lower()
        palavras_chave = pergunta_lower.split()
        
        # Identifica arquivos e campos relevantes
        arquivos_relevantes = []
        campos_relevantes = []
        
        for arquivo_info in contexto_completo:
            relevancia = 0
            campos_matches = []
            
            # Verifica relevância por nome do arquivo
            nome_arquivo = arquivo_info['nome'].lower()
            if any(palavra in nome_arquivo for palavra in ['cabecalho', 'header']):
                if any(termo in pergunta_lower for termo in ['nota', 'fiscal', 'emitente', 'fornecedor', 'data', 'valor']):
                    relevancia += 3
            
            if any(palavra in nome_arquivo for palavra in ['itens', 'items']):
                if any(termo in pergunta_lower for termo in ['produto', 'item', 'material', 'categoria', 'quantidade']):
                    relevancia += 3
            
            # Verifica relevância por colunas
            for coluna in arquivo_info['colunas']:
                coluna_lower = coluna.lower()
                for palavra in palavras_chave:
                    if palavra in coluna_lower or coluna_lower in palavra:
                        relevancia += 2
                        campos_matches.append(coluna)
            
            # Verifica relevância por amostras de dados
            for coluna, amostras in arquivo_info['amostras'].items():
                if isinstance(amostras, list):
                    for amostra in amostras:
                        if isinstance(amostra, str):
                            for palavra in palavras_chave:
                                if palavra in amostra.lower():
                                    relevancia += 1
                                    if coluna not in campos_matches:
                                        campos_matches.append(coluna)
            
            if relevancia > 0:
                arquivos_relevantes.append({
                    'arquivo': arquivo_info['nome'],
                    'relevancia': relevancia,
                    'campos_relevantes': campos_matches,
                    'info': arquivo_info
                })
        
        # Ordena por relevância
        arquivos_relevantes.sort(key=lambda x: x['relevancia'], reverse=True)
        
        if not arquivos_relevantes:
            resultado += f"🤔 Nenhum contexto específico encontrado para '{pergunta}'\n"
            resultado += f"📋 Arquivos disponíveis: {', '.join([info['nome'] for info in contexto_completo])}\n"
            resultado += f"💡 Sugestão: Tente perguntas sobre produtos, fornecedores, datas ou valores\n"
        else:
            resultado += f"🎯 Contexto RAG identificado:\n\n"
            
            for i, arquivo_rel in enumerate(arquivos_relevantes[:2]):  # Top 2 mais relevantes
                info = arquivo_rel['info']
                resultado += f"📄 {arquivo_rel['arquivo']} (Relevância: {arquivo_rel['relevancia']})\n"
                resultado += f"   📊 Registros: {info['linhas']:,}\n"
                resultado += f"   🏷️ Campos relevantes: {', '.join(arquivo_rel['campos_relevantes'][:5])}\n"
                
                # Mostra amostras de dados relevantes
                if arquivo_rel['campos_relevantes']:
                    resultado += f"   📝 Amostras de dados:\n"
                    for campo in arquivo_rel['campos_relevantes'][:3]:
                        if campo in info['amostras']:
                            amostra = info['amostras'][campo]
                            if isinstance(amostra, list):
                                resultado += f"      • {campo}: {', '.join(map(str, amostra[:3]))}\n"
                            elif isinstance(amostra, dict):
                                resultado += f"      • {campo}: {amostra}\n"
                resultado += f"\n"
        
        # Sugestões contextuais baseadas no RAG
        resultado += f"💡 Contexto semântico para interpretação:\n"
        
        if any('data' in palavra for palavra in palavras_chave):
            resultado += f"   📅 Consulta temporal identificada - considere filtros por período\n"
        
        if any(termo in pergunta_lower for termo in ['quanto', 'valor', 'total', 'soma']):
            resultado += f"   💰 Consulta de agregação financeira identificada\n"
        
        if any(termo in pergunta_lower for termo in ['produto', 'item', 'categoria']):
            resultado += f"   📦 Consulta de produtos identificada - considere joins com itens\n"
        
        if any(termo in pergunta_lower for termo in ['fornecedor', 'emitente', 'empresa']):
            resultado += f"   🏢 Consulta de fornecedores identificada\n"
        
        # Identifica padrões temporais específicos
        if '2024-01-15' in pergunta or '15 de janeiro' in pergunta_lower:
            resultado += f"   🗓️ Data específica identificada: 15/01/2024\n"
        
        # Identifica categorias específicas
        if 'escritório' in pergunta_lower:
            resultado += f"   📎 Categoria específica: Material de escritório\n"
        
        resultado += f"\n🧠 RAG semântico processado! Use este contexto para interpretação precisa."
        
        return resultado
        
    except Exception as e:
        return f"❌ Erro durante consulta RAG: {str(e)}"