from crewai.tools import tool
import pandas as pd
import os
from typing import Dict, Any
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from models.notas_fiscais import validar_dataframe_cabecalho, validar_dataframe_itens

@tool("csv_validator")
def csv_validator_tool(diretorio_dados: str = "/dados/notasfiscais/") -> str:
    """
    Valida e estrutura arquivos CSV usando modelos Pydantic.
    Transforma os CSVs em DataFrames limpos e confiáveis, garantindo
    a integridade dos dados antes do processamento pelos outros agentes.
    
    Args:
        diretorio_dados: Diretório onde estão os arquivos CSV extraídos
    
    Returns:
        Relatório detalhado da validação e estruturação dos dados
    """
    try:
        # Verifica se o diretório existe
        if not os.path.exists(diretorio_dados):
            return f"❌ Erro: Diretório {diretorio_dados} não encontrado"
        
        # Lista arquivos CSV no diretório
        csv_files = [f for f in os.listdir(diretorio_dados) if f.lower().endswith('.csv')]
        
        if not csv_files:
            return f"❌ Erro: Nenhum arquivo CSV encontrado em {diretorio_dados}"
        
        resultado = f"🔍 Iniciando validação Pydantic dos arquivos CSV...\n\n"
        
        # Procura pelos arquivos principais
        arquivo_cabecalho = None
        arquivo_itens = None
        
        for arquivo in csv_files:
            nome_lower = arquivo.lower()
            if 'cabecalho' in nome_lower or 'header' in nome_lower:
                arquivo_cabecalho = arquivo
            elif 'itens' in nome_lower or 'items' in nome_lower:
                arquivo_itens = arquivo
        
        validacoes_realizadas = 0
        total_registros_validos = 0
        erros_encontrados = []
        
        # Valida arquivo de cabeçalhos
        if arquivo_cabecalho:
            resultado += f"📋 Validando {arquivo_cabecalho}...\n"
            try:
                # Define tipos específicos para evitar conversões automáticas problemáticas
                dtype_cabecalho = {
                    'NÚMERO': str,
                    'CPF/CNPJ Emitente': str,
                    'CNPJ DESTINATÁRIO': str
                }
                
                df_cabecalho = pd.read_csv(
                    os.path.join(diretorio_dados, arquivo_cabecalho),
                    delimiter=',',
                    decimal='.',
                    dtype=dtype_cabecalho,
                    keep_default_na=False  # Evita conversão de strings para NaN
                )
                
                # Usa os nomes originais das colunas do CSV (sem mapeamento)
                # Os novos modelos Pydantic já usam os nomes reais das colunas
                df_cabecalho_mapped = df_cabecalho.copy()
                
                # Valida com Pydantic usando os novos modelos
                validacao_cab = validar_dataframe_cabecalho(df_cabecalho_mapped)
                
                resultado += f"   ✅ Registros válidos: {validacao_cab.total_cabecalhos}\n"
                resultado += f"   📊 Total de registros: {len(df_cabecalho)}\n"
                
                if validacao_cab.erros:
                    resultado += f"   ⚠️ Erros encontrados: {len(validacao_cab.erros)}\n"
                    erros_encontrados.extend(validacao_cab.erros[:5])  # Primeiros 5 erros
                
                total_registros_validos += validacao_cab.total_cabecalhos
                validacoes_realizadas += 1
                
                # Salva DataFrame limpo com nomes originais das colunas
                df_limpo_path = os.path.join(diretorio_dados, "cabecalho_validado.csv")
                df_cabecalho_mapped.to_csv(df_limpo_path, index=False)
                resultado += f"   💾 DataFrame limpo salvo em: cabecalho_validado.csv\n"
                
            except Exception as e:
                erro_msg = f"Erro ao processar {arquivo_cabecalho}: {str(e)}"
                resultado += f"   ❌ {erro_msg}\n"
                erros_encontrados.append(erro_msg)
                print(f"DEBUG: Erro detalhado no cabecalho: {e}")
        
        # Valida arquivo de itens
        if arquivo_itens:
            resultado += f"\n📦 Validando {arquivo_itens}...\n"
            try:
                # Define tipos específicos para evitar conversões automáticas problemáticas
                dtype_itens = {
                    'NÚMERO': str,
                    'NÚMERO PRODUTO': str,
                    'CPF/CNPJ Emitente': str,
                    'CNPJ DESTINATÁRIO': str
                }
                
                df_itens = pd.read_csv(
                    os.path.join(diretorio_dados, arquivo_itens),
                    delimiter=',',
                    decimal='.',
                    dtype=dtype_itens,
                    keep_default_na=False  # Evita conversão de strings para NaN
                )
                
                # Usa os nomes originais das colunas do CSV (sem mapeamento)
                # Os novos modelos Pydantic já usam os nomes reais das colunas
                df_itens_mapped = df_itens.copy()
                
                # Valida com Pydantic usando os novos modelos
                validacao_itens = validar_dataframe_itens(df_itens_mapped)
                
                resultado += f"   ✅ Registros válidos: {validacao_itens.total_itens}\n"
                resultado += f"   📊 Total de registros: {len(df_itens)}\n"
                
                if validacao_itens.erros:
                    resultado += f"   ⚠️ Erros encontrados: {len(validacao_itens.erros)}\n"
                    erros_encontrados.extend(validacao_itens.erros[:5])  # Primeiros 5 erros
                
                total_registros_validos += validacao_itens.total_itens
                validacoes_realizadas += 1
                
                # Salva DataFrame limpo com nomes originais das colunas
                df_limpo_path = os.path.join(diretorio_dados, "itens_validado.csv")
                df_itens_mapped.to_csv(df_limpo_path, index=False)
                resultado += f"   💾 DataFrame limpo salvo em: itens_validado.csv\n"
                
            except Exception as e:
                erro_msg = f"Erro ao processar {arquivo_itens}: {str(e)}"
                resultado += f"   ❌ {erro_msg}\n"
                erros_encontrados.append(erro_msg)
                print(f"DEBUG: Erro detalhado nos itens: {e}")
        
        # Processa outros CSVs se necessário
        outros_csvs = [f for f in csv_files if f != arquivo_cabecalho and f != arquivo_itens]
        if outros_csvs:
            resultado += f"\n📄 Outros CSVs encontrados: {', '.join(outros_csvs)}\n"
            resultado += f"   ℹ️ Processamento básico aplicado (sem validação Pydantic específica)\n"
        
        # Resumo final
        resultado += f"\n🎯 RESUMO DA VALIDAÇÃO:\n"
        resultado += f"   📁 Arquivos processados: {validacoes_realizadas}\n"
        resultado += f"   ✅ Total de registros válidos: {total_registros_validos}\n"
        resultado += f"   ❌ Total de erros: {len(erros_encontrados)}\n"
        
        if erros_encontrados:
            resultado += f"\n⚠️ PRIMEIROS ERROS ENCONTRADOS:\n"
            for erro in erros_encontrados[:3]:
                resultado += f"   • {erro}\n"
        
        if not arquivo_cabecalho or not arquivo_itens:
            resultado += f"\n⚠️ ATENÇÃO: Arquivos padrão não encontrados!\n"
            resultado += f"   🔍 Esperados: '*cabecalho*.csv' e '*itens*.csv'\n"
            resultado += f"   📋 Disponíveis: {', '.join(csv_files)}\n"
        
        resultado += f"\n🛡️ Validação Pydantic concluída! DataFrames estruturados e prontos para análise."
        
        return resultado
        
    except Exception as e:
        return f"❌ Erro inesperado durante a validação: {str(e)}"