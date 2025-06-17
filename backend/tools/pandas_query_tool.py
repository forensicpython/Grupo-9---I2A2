from crewai.tools import tool
import pandas as pd
import os
from datetime import datetime
import json
import numpy as np
from decimal import Decimal, getcontext

# Define precisão matemática para cálculos financeiros
getcontext().prec = 28

@tool("pandas_query_executor")
def pandas_query_executor_tool(query_description: str, diretorio_dados: str = None) -> str:
    """
    Executa operações Pandas sobre os dados validados de notas fiscais.
    Suporta operações como groupby, sum, filter, mean, join entre cabeçalhos e itens.
    Esta ferramenta trabalha com dados já validados pelo Guardião Pydantic.
    
    Args:
        query_description: Descrição da consulta em linguagem natural
        diretorio_dados: Diretório onde estão os arquivos CSV validados
    
    Returns:
        Resultado da consulta com dados estruturados e formatados
    """
    try:
        # Define diretório padrão se não fornecido
        if diretorio_dados is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            diretorio_dados = os.path.join(base_dir, 'dados', 'notasfiscais')
        
        # Verifica se o diretório existe
        if not os.path.exists(diretorio_dados):
            return f"❌ Erro: Diretório {diretorio_dados} não encontrado"
        
        # Carrega dados validados
        df_cabecalho = None
        df_itens = None
        
        # Lista todos os CSVs disponíveis
        csv_files = [f for f in os.listdir(diretorio_dados) if f.endswith('.csv')]
        
        # Prioriza arquivos validados (com colunas já mapeadas)
        for arquivo in csv_files:
            arquivo_lower = arquivo.lower()
            caminho_arquivo = os.path.join(diretorio_dados, arquivo)
            
            if 'cabecalho_validado' in arquivo_lower:
                df_cabecalho = pd.read_csv(caminho_arquivo)
                # Converte data_emissao se existir e for string
                if 'data_emissao' in df_cabecalho.columns:
                    try:
                        df_cabecalho['data_emissao'] = pd.to_datetime(df_cabecalho['data_emissao'])
                    except:
                        pass
                        
            elif 'itens_validado' in arquivo_lower:
                df_itens = pd.read_csv(caminho_arquivo)
                
            elif df_cabecalho is None and ('cabecalho' in arquivo_lower or 'header' in arquivo_lower):
                df_cabecalho = pd.read_csv(caminho_arquivo)
                # Tenta mapear colunas do CSV original
                mapeamento_cabecalho = {
                    'NÚMERO': 'numero_nf',
                    'DATA EMISSÃO': 'data_emissao', 
                    'CPF/CNPJ Emitente': 'cnpj_emitente',
                    'RAZÃO SOCIAL EMITENTE': 'nome_emitente',
                    'VALOR NOTA FISCAL': 'valor_total',
                    'UF EMITENTE': 'estado',
                    'MUNICÍPIO EMITENTE': 'cidade'
                }
                for col_original, col_nova in mapeamento_cabecalho.items():
                    if col_original in df_cabecalho.columns:
                        df_cabecalho = df_cabecalho.rename(columns={col_original: col_nova})
                if 'data_emissao' in df_cabecalho.columns:
                    try:
                        df_cabecalho['data_emissao'] = pd.to_datetime(df_cabecalho['data_emissao'])
                    except:
                        pass
                        
            elif df_itens is None and ('itens' in arquivo_lower or 'items' in arquivo_lower):
                df_itens = pd.read_csv(caminho_arquivo)
                # Tenta mapear colunas do CSV original
                mapeamento_itens = {
                    'NÚMERO': 'numero_nf',
                    'NÚMERO PRODUTO': 'codigo_produto',
                    'DESCRIÇÃO DO PRODUTO/SERVIÇO': 'descricao_produto', 
                    'QUANTIDADE': 'quantidade',
                    'VALOR UNITÁRIO': 'valor_unitario',
                    'VALOR TOTAL': 'valor_total_item',
                    'NCM/SH (TIPO DE PRODUTO)': 'categoria'
                }
                for col_original, col_nova in mapeamento_itens.items():
                    if col_original in df_itens.columns:
                        df_itens = df_itens.rename(columns={col_original: col_nova})
                
        # Se não encontrou pelos nomes, tenta identificar pela estrutura
        if df_cabecalho is None or df_itens is None:
            for arquivo in csv_files:
                caminho_arquivo = os.path.join(diretorio_dados, arquivo)
                df_temp = pd.read_csv(caminho_arquivo, nrows=5)
                
                # Arquivo de cabeçalho geralmente tem menos linhas e não tem "PRODUTO"
                if df_cabecalho is None and 'PRODUTO' not in ' '.join(df_temp.columns).upper():
                    df_cabecalho = pd.read_csv(caminho_arquivo)
                    for col in df_cabecalho.columns:
                        if 'data' in col.lower() and 'emiss' in col.lower():
                            df_cabecalho['data_emissao'] = pd.to_datetime(df_cabecalho[col])
                            break
                            
                # Arquivo de itens geralmente tem "PRODUTO" nas colunas
                elif df_itens is None and 'PRODUTO' in ' '.join(df_temp.columns).upper():
                    df_itens = pd.read_csv(caminho_arquivo)
        
        if df_cabecalho is None and df_itens is None:
            return "❌ Erro: Nenhum arquivo de dados encontrado"
        
        # Analisa a query e executa operações
        query_lower = query_description.lower()
        resultado = f"📊 Executando consulta: {query_description}\n\n"
        
        # Informações básicas dos dados
        if df_cabecalho is not None:
            resultado += f"📋 Total de notas fiscais: {len(df_cabecalho)}\n"
            
        if df_itens is not None:
            resultado += f"📦 Total de itens: {len(df_itens)}\n\n"
        
        # SEMPRE PRIORIZAR ANÁLISE DE FORNECEDORES QUANDO MENCIONADOS
        # Responde sobre quantas notas fiscais existem
        if any(termo in query_lower for termo in ['quantas', 'quantidade', 'número', 'total']) and any(termo in query_lower for termo in ['notas', 'fiscal', 'nf']):
            # Se mencionou fornecedores, VAI PARA A SEÇÃO DE FORNECEDORES
            if any(termo in query_lower for termo in ['fornecedor', 'fornecedores', 'emitente', 'principais']):
                pass  # Continua para a seção de fornecedores
            elif df_cabecalho is not None:
                total_notas = len(df_cabecalho)
                resultado += f"📄 **Total de notas fiscais no arquivo: {total_notas}**\n\n"
                
                # Estatísticas adicionais
                if 'data_emissao' in df_cabecalho.columns:
                    periodo_inicio = df_cabecalho['data_emissao'].min().strftime('%d/%m/%Y')
                    periodo_fim = df_cabecalho['data_emissao'].max().strftime('%d/%m/%Y')
                    resultado += f"📅 Período: {periodo_inicio} a {periodo_fim}\n"
                
                # Valor total se existir coluna de valor
                if 'valor_total' in df_cabecalho.columns:
                    valor_total = df_cabecalho['valor_total'].sum()
                    resultado += f"💰 Valor total das notas: R$ {valor_total:,.2f}\n"
                elif 'VALOR NOTA FISCAL' in df_cabecalho.columns:
                    valor_total = df_cabecalho['VALOR NOTA FISCAL'].sum()
                    resultado += f"💰 Valor total das notas: R$ {valor_total:,.2f}\n"
                        
                return resultado
        
        # Análise de fornecedores se solicitado (SEMPRE ATIVAR QUANDO HOUVER "PRINCIPAIS FORNECEDORES")
        if (any(termo in query_lower for termo in ['fornecedor', 'fornecedores', 'emitente', 'principais']) or 
            ('principais' in query_lower and 'fornece' in query_lower)) and df_cabecalho is not None:
            
            # Identifica colunas de fornecedor, valor e CNPJ
            nome_col = None
            valor_col = None
            cnpj_col = None
            
            for col in df_cabecalho.columns:
                if col in ['nome_emitente', 'RAZÃO SOCIAL EMITENTE']:
                    nome_col = col
                elif col in ['valor_total', 'VALOR NOTA FISCAL']:
                    valor_col = col
                elif col in ['cnpj_emitente', 'CPF/CNPJ Emitente']:
                    cnpj_col = col
            
            if nome_col and valor_col:
                # Agrupamento com nome, CNPJ e valores
                if cnpj_col:
                    # Cria um DataFrame agrupado com nome, CNPJ e totais - PRECISÃO MATEMÁTICA
                    # Converte para Decimal para precisão financeira
                    df_temp = df_cabecalho.copy()
                    df_temp[valor_col] = df_temp[valor_col].apply(lambda x: Decimal(str(x)) if pd.notna(x) else Decimal('0'))
                    
                    grupo_fornecedores = df_temp.groupby([nome_col, cnpj_col]).agg({
                        valor_col: ['sum', 'count']
                    })
                    
                    # Converte de volta para float para display, mantendo precisão
                    grupo_fornecedores.loc[:, (valor_col, 'sum')] = grupo_fornecedores[valor_col, 'sum'].apply(lambda x: round(float(x), 2))
                    
                    # Ordena por valor total (descendente)
                    grupo_fornecedores_valor = grupo_fornecedores.sort_values((valor_col, 'sum'), ascending=False)
                    
                    # Ordena por quantidade de notas (descendente)
                    grupo_fornecedores_qtd = grupo_fornecedores.sort_values((valor_col, 'count'), ascending=False)
                    
                    resultado += f"\n🏢 **PRINCIPAIS FORNECEDORES:**\n\n"
                    
                    # Lista por valor total
                    resultado += f"💰 **Por Valor Total das Notas Fiscais:**\n"
                    for i, ((nome, cnpj), dados) in enumerate(grupo_fornecedores_valor.head(10).iterrows(), 1):
                        valor_total = dados[(valor_col, 'sum')]
                        qtd_notas = int(dados[(valor_col, 'count')])
                        # Formata CNPJ
                        cnpj_str = str(cnpj)
                        cnpj_formatado = f"{cnpj_str[:2]}.{cnpj_str[2:5]}.{cnpj_str[5:8]}/{cnpj_str[8:12]}-{cnpj_str[12:14]}" if len(cnpj_str) == 14 else cnpj
                        resultado += f"   {i}. **{nome}** ({cnpj_formatado}) - R$ {valor_total:,.2f} ({qtd_notas} {'nota' if qtd_notas == 1 else 'notas'})\n"
                    
                    # Lista por quantidade de notas
                    resultado += f"\n📊 **Por Quantidade de Notas Fiscais:**\n"
                    for i, ((nome, cnpj), dados) in enumerate(grupo_fornecedores_qtd.head(10).iterrows(), 1):
                        valor_total = dados[(valor_col, 'sum')]
                        qtd_notas = int(dados[(valor_col, 'count')])
                        # Formata CNPJ
                        cnpj_str = str(cnpj)
                        cnpj_formatado = f"{cnpj_str[:2]}.{cnpj_str[2:5]}.{cnpj_str[5:8]}/{cnpj_str[8:12]}-{cnpj_str[12:14]}" if len(cnpj_str) == 14 else cnpj
                        resultado += f"   {i}. **{nome}** ({cnpj_formatado}) - {qtd_notas} {'nota' if qtd_notas == 1 else 'notas'} - R$ {valor_total:,.2f}\n"
                        
                else:
                    # Fallback sem CNPJ
                    top_fornecedores_qtd = df_cabecalho[nome_col].value_counts().head(10)
                    top_fornecedores_valor = df_cabecalho.groupby(nome_col)[valor_col].sum().sort_values(ascending=False).head(10)
                    
                    resultado += f"\n🏢 **PRINCIPAIS FORNECEDORES:**\n\n"
                    resultado += f"📊 **Por Quantidade de Notas Fiscais:**\n"
                    for i, (fornecedor, qtd) in enumerate(top_fornecedores_qtd.items(), 1):
                        resultado += f"   {i}. {fornecedor}: {qtd} notas\n"
                    
                    resultado += f"\n💰 **Por Valor Total:**\n"
                    for i, (fornecedor, valor) in enumerate(top_fornecedores_valor.items(), 1):
                        resultado += f"   {i}. {fornecedor}: R$ {valor:,.2f}\n"
                
                # Valor total geral e estatísticas
                valor_total_geral = df_cabecalho[valor_col].sum()
                total_fornecedores = df_cabecalho[nome_col].nunique()
                resultado += f"\n💵 **RESUMO GERAL:**\n"
                resultado += f"   • Valor total de todas as notas: R$ {valor_total_geral:,.2f}\n"
                resultado += f"   • Total de fornecedores únicos: {total_fornecedores}\n"
                resultado += f"   • Total de notas fiscais: {len(df_cabecalho)}\n"
                
                return resultado
        
        # Operações de busca por categoria/produto
        if ('escritório' in query_lower or 'material' in query_lower) and df_itens is not None:
            # Procura colunas de descrição e valor
            desc_col = None
            valor_col = None
            
            for col in df_itens.columns:
                if 'produto' in col.lower() or 'descri' in col.lower():
                    desc_col = col
                if 'valor' in col.lower() and 'total' in col.lower():
                    valor_col = col
            
            if desc_col:
                # Filtra itens relacionados a escritório
                filtro_escritorio = df_itens[
                    df_itens[desc_col].str.contains('escritório|papel|caneta|lápis|caderno', case=False, na=False)
                ]
                
                if len(filtro_escritorio) > 0:
                    resultado += f"📦 Itens de escritório encontrados: {len(filtro_escritorio)}\n"
                    
                    if valor_col:
                        valor_total_escritorio = filtro_escritorio[valor_col].sum()
                        resultado += f"💰 Valor total em itens de escritório: R$ {valor_total_escritorio:,.2f}\n"
                        
                        # Top produtos
                        top_produtos = filtro_escritorio.groupby(desc_col)[valor_col].sum().sort_values(ascending=False).head(3)
                        resultado += f"\n📋 Top 3 produtos de escritório:\n"
                        for produto, valor in top_produtos.items():
                            resultado += f"   • {produto}: R$ {valor:,.2f}\n"
        
        # Operações de agregação por estado
        if 'estado' in query_lower and df_cabecalho is not None:
            if 'estado' in df_cabecalho.columns:
                por_estado = df_cabecalho.groupby('estado').agg({
                    'valor_total': ['sum', 'count'],
                    'numero_nf': 'count'
                }).round(2)
                
                resultado += f"\n🗺️ Análise por Estado:\n"
                for estado in por_estado.index:
                    valor_total = por_estado.loc[estado, ('valor_total', 'sum')]
                    qtd_nfs = por_estado.loc[estado, ('valor_total', 'count')]
                    resultado += f"   • {estado}: R$ {valor_total:,.2f} ({qtd_nfs} NFs)\n"
        
        # Operações de comparação temporal
        if 'comparar' in query_lower and 'semana' in query_lower and df_cabecalho is not None:
            # Compara mesma data da semana anterior
            data_base = pd.to_datetime('2024-01-15')
            data_anterior = data_base - pd.Timedelta(days=7)
            
            df_atual = df_cabecalho[df_cabecalho['data_emissao'].dt.date == data_base.date()]
            df_anterior = df_cabecalho[df_cabecalho['data_emissao'].dt.date == data_anterior.date()]
            
            valor_atual = df_atual['valor_total'].sum()
            valor_anterior = df_anterior['valor_total'].sum()
            
            diferenca = valor_atual - valor_anterior
            percentual = (diferenca / valor_anterior * 100) if valor_anterior > 0 else 0
            
            resultado += f"\n📈 Comparação Temporal:\n"
            resultado += f"   • {data_base.strftime('%d/%m/%Y')}: R$ {valor_atual:,.2f}\n"
            resultado += f"   • {data_anterior.strftime('%d/%m/%Y')}: R$ {valor_anterior:,.2f}\n"
            resultado += f"   • Diferença: R$ {diferenca:,.2f} ({percentual:+.1f}%)\n"
        
        # SEMPRE FORÇA ANÁLISE DETALHADA DE FORNECEDORES PARA QUALQUER QUERY RELACIONADA
        if df_cabecalho is not None and (
            any(termo in query_lower for termo in ['maiores', 'maior', 'comprador', 'compradores', 'vendedor', 'vendedores', 'fornecedor', 'fornecedores', 'emitente', 'principais']) or
            any(termo in query_lower for termo in ['cnpj', 'empresa', 'empresas']) or
            'valor gasto' in query_lower or 'numero de notas' in query_lower or
            'notas fiscais' in query_lower or 'valor total' in query_lower or
            'emitidas' in query_lower or 'valor' in query_lower
        ):
            
            # IDENTIFICA COLUNAS NO DATASET REAL PARA VENDEDORES (EMITENTES) E COMPRADORES (DESTINATÁRIOS)
            
            # Colunas para VENDEDORES (Emitentes)
            nome_emitente_col = 'RAZÃO SOCIAL EMITENTE' if 'RAZÃO SOCIAL EMITENTE' in df_cabecalho.columns else None
            cnpj_emitente_col = 'CPF/CNPJ Emitente' if 'CPF/CNPJ Emitente' in df_cabecalho.columns else None
            
            # Colunas para COMPRADORES (Destinatários)
            nome_destinatario_col = 'NOME DESTINATÁRIO' if 'NOME DESTINATÁRIO' in df_cabecalho.columns else None
            cnpj_destinatario_col = 'CNPJ DESTINATÁRIO' if 'CNPJ DESTINATÁRIO' in df_cabecalho.columns else None
            
            # Coluna de valor
            valor_col = 'VALOR NOTA FISCAL' if 'VALOR NOTA FISCAL' in df_cabecalho.columns else None
            
            if valor_col and (nome_emitente_col or nome_destinatario_col):
                df_temp = df_cabecalho.copy()
                
                # Converte valores para Decimal para precisão financeira
                df_temp[valor_col] = df_temp[valor_col].apply(lambda x: Decimal(str(x)) if pd.notna(x) else Decimal('0'))
                
                resultado += f"\n🏆 **ANÁLISE DOS DADOS REAIS - JANEIRO 2024:**\n\n"
                
                # ANÁLISE DOS COMPRADORES (DESTINATÁRIOS)
                if nome_destinatario_col and cnpj_destinatario_col:
                    # Remove linhas com destinatários vazios/nulos
                    df_compradores = df_temp.dropna(subset=[nome_destinatario_col, cnpj_destinatario_col])
                    df_compradores = df_compradores[df_compradores[nome_destinatario_col] != '']
                    
                    if len(df_compradores) > 0:
                        grupo_compradores = df_compradores.groupby([nome_destinatario_col, cnpj_destinatario_col]).agg({
                            valor_col: ['sum', 'count']
                        })
                        
                        # Converte para display
                        grupo_compradores.loc[:, (valor_col, 'sum')] = grupo_compradores[valor_col, 'sum'].apply(lambda x: round(float(x), 2))
                        
                        # Ordena por valor (maiores compradores)
                        grupo_compradores_valor = grupo_compradores.sort_values((valor_col, 'sum'), ascending=False)
                        
                        resultado += f"💰 **MAIORES COMPRADORES EM VALOR GASTO:**\n"
                        for i, ((nome, cnpj), dados) in enumerate(grupo_compradores_valor.head(5).iterrows(), 1):
                            valor_total = dados[(valor_col, 'sum')]
                            qtd_notas = int(dados[(valor_col, 'count')])
                            # Formata CNPJ corretamente
                            cnpj_str = str(cnpj)
                            cnpj_formatado = f"{cnpj_str[:2]}.{cnpj_str[2:5]}.{cnpj_str[5:8]}/{cnpj_str[8:12]}-{cnpj_str[12:14]}" if len(cnpj_str) == 14 else cnpj
                            resultado += f"   {i}. **{nome}** ({cnpj_formatado}) - R$ {valor_total:,.2f} ({qtd_notas} notas)\n"
                    else:
                        resultado += f"💰 **MAIORES COMPRADORES EM VALOR GASTO:**\n"
                        resultado += f"   ⚠️ Não foram encontrados dados de destinatários válidos\n"
                
                # ANÁLISE DOS VENDEDORES (EMITENTES)
                if nome_emitente_col and cnpj_emitente_col:
                    grupo_vendedores = df_temp.groupby([nome_emitente_col, cnpj_emitente_col]).agg({
                        valor_col: ['sum', 'count']
                    })
                    
                    # Converte para display
                    grupo_vendedores.loc[:, (valor_col, 'sum')] = grupo_vendedores[valor_col, 'sum'].apply(lambda x: round(float(x), 2))
                    
                    # Ordena por quantidade de notas (maiores vendedores)
                    grupo_vendedores_qtd = grupo_vendedores.sort_values((valor_col, 'count'), ascending=False)
                    
                    resultado += f"\n📊 **MAIORES VENDEDORES EM NÚMERO DE NOTAS FISCAIS:**\n"
                    for i, ((nome, cnpj), dados) in enumerate(grupo_vendedores_qtd.head(5).iterrows(), 1):
                        valor_total = dados[(valor_col, 'sum')]
                        qtd_notas = int(dados[(valor_col, 'count')])
                        # Formata CNPJ corretamente
                        cnpj_str = str(cnpj)
                        cnpj_formatado = f"{cnpj_str[:2]}.{cnpj_str[2:5]}.{cnpj_str[5:8]}/{cnpj_str[8:12]}-{cnpj_str[12:14]}" if len(cnpj_str) == 14 else cnpj
                        resultado += f"   {i}. **{nome}** ({cnpj_formatado}) - {qtd_notas} notas (R$ {valor_total:,.2f})\n"
                
                # RESUMO GERAL
                valor_total_geral = df_cabecalho[valor_col].sum()
                resultado += f"\n💵 **RESUMO GERAL:**\n"
                resultado += f"   • Valor total das notas fiscais: R$ {valor_total_geral:,.2f}\n"
                resultado += f"   • Total de notas fiscais: {len(df_cabecalho)}\n"
                # Conta empresas únicas (emitentes ou destinatários)
                if nome_emitente_col:
                    resultado += f"   • Total de empresas emitentes únicas: {df_cabecalho[nome_emitente_col].nunique()}\n"
                if nome_destinatario_col:
                    resultado += f"   • Total de empresas destinatárias únicas: {df_cabecalho[nome_destinatario_col].nunique()}\n"
                
                # Período dos dados
                if 'DATA EMISSÃO' in df_cabecalho.columns:
                    try:
                        df_temp_data = df_cabecalho.copy()
                        df_temp_data['DATA EMISSÃO'] = pd.to_datetime(df_temp_data['DATA EMISSÃO'])
                        data_min = df_temp_data['DATA EMISSÃO'].min().strftime('%d/%m/%Y')
                        data_max = df_temp_data['DATA EMISSÃO'].max().strftime('%d/%m/%Y')
                        resultado += f"   • Período: {data_min} a {data_max}\n"
                    except:
                        pass
                
                return resultado
        
        # NUNCA DEVE CHEGAR AQUI SE HÁ FORNECEDORES - DEBUG
        print(f"DEBUG: Query não capturada: '{query_description}'")
        print(f"DEBUG: Termos encontrados: {[t for t in ['fornecedor', 'fornecedores', 'emitente', 'principais'] if t in query_lower]}")
        
        # Estatísticas gerais se nenhuma operação específica foi identificada
        if not any(termo in query_lower for termo in ['data', 'escritório', 'estado', 'comparar', 'fornecedor', 'fornecedores', 'emitente', 'principais']):
            if df_cabecalho is not None:
                # Identifica coluna de valor
                valor_col = 'valor_total' if 'valor_total' in df_cabecalho.columns else 'VALOR NOTA FISCAL'
                data_col = 'data_emissao' if 'data_emissao' in df_cabecalho.columns else 'DATA EMISSÃO'
                
                resultado += f"📊 Estatísticas Gerais - Cabeçalhos:\n"
                resultado += f"   • Total de notas fiscais: {len(df_cabecalho):,}\n"
                
                if valor_col in df_cabecalho.columns:
                    resultado += f"   • Valor total geral: R$ {df_cabecalho[valor_col].sum():,.2f}\n"
                    resultado += f"   • Valor médio por NF: R$ {df_cabecalho[valor_col].mean():,.2f}\n"
                    
                if data_col in df_cabecalho.columns:
                    try:
                        data_min = pd.to_datetime(df_cabecalho[data_col]).min().strftime('%d/%m/%Y')
                        data_max = pd.to_datetime(df_cabecalho[data_col]).max().strftime('%d/%m/%Y')
                        resultado += f"   • Período: {data_min} a {data_max}\n"
                    except:
                        pass
            
            if df_itens is not None:
                valor_item_col = 'valor_total_item' if 'valor_total_item' in df_itens.columns else 'VALOR TOTAL'
                qtd_col = 'quantidade' if 'quantidade' in df_itens.columns else 'QUANTIDADE'
                
                resultado += f"\n📦 Estatísticas Gerais - Itens:\n"
                resultado += f"   • Total de itens: {len(df_itens):,}\n"
                
                if valor_item_col in df_itens.columns:
                    resultado += f"   • Valor total dos itens: R$ {df_itens[valor_item_col].sum():,.2f}\n"
                    
                if qtd_col in df_itens.columns:
                    resultado += f"   • Quantidade total: {df_itens[qtd_col].sum():,.0f}\n"
        
        # Join entre cabeçalhos e itens se ambos existem
        if df_cabecalho is not None and df_itens is not None and 'detalhado' in query_lower:
            numero_col_cab = 'numero_nf' if 'numero_nf' in df_cabecalho.columns else 'NÚMERO'
            numero_col_itens = 'numero_nf' if 'numero_nf' in df_itens.columns else 'NÚMERO'
            
            try:
                df_completo = pd.merge(df_itens, df_cabecalho, left_on=numero_col_itens, right_on=numero_col_cab, how='left')
                resultado += f"\n🔗 Dados combinados (Cabeçalhos + Itens):\n"
                resultado += f"   • Registros combinados: {len(df_completo):,}\n"
                resultado += f"   • Cobertura do join: {(len(df_completo) / len(df_itens) * 100):.1f}%\n"
            except Exception as e:
                resultado += f"\n⚠️ Erro no join: {str(e)}\n"
        
        resultado += f"\n✅ Consulta Pandas executada com sucesso!"
        
        return resultado
        
    except Exception as e:
        return f"❌ Erro durante execução da consulta Pandas: {str(e)}"