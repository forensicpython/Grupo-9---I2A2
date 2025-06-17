#!/usr/bin/env python3
"""
Instaprice - Sistema Inteligente de Análise de Notas Fiscais
Versão melhorada com tratamento de erros, logging e ESPIONAGEM DE AGENTES 🕵️
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Adiciona o diretório atual ao path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from instaprice import Instaprice
from utils.logger import setup_logger, log_execution_step, log_error_with_context
from tools.agent_surveillance import criar_espiao_instaprice, interceptar_conversas_instaprice

def validate_environment():
    """Valida configuração do ambiente"""
    logger = setup_logger()
    
    # Procura arquivo .env no diretório atual e no pai
    env_paths = [
        '.env',  # Diretório atual
        '../.env',  # Diretório pai
        os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')  # Caminho absoluto para o pai
    ]
    
    env_found = False
    for env_path in env_paths:
        if os.path.exists(env_path):
            logger.info(f"✅ Arquivo .env encontrado em: {env_path}")
            load_dotenv(env_path)
            env_found = True
            break
    
    if not env_found:
        logger.error("❌ Arquivo .env não encontrado em nenhum local esperado.")
        logger.error("Locais verificados: " + ", ".join(env_paths))
        return False
    
    # Verifica GROQ_API_KEY
    groq_key = os.getenv('GROQ_API_KEY')
    if not groq_key or groq_key == 'your_groq_api_key_here':
        logger.error("❌ GROQ_API_KEY não configurada no arquivo .env")
        return False
    
    logger.info("✅ Ambiente validado com sucesso")
    return True

def executar_instaprice_com_analise(inputs):
    """Função wrapper para executar Instaprice (usada pelo interceptador)"""
    instaprice = Instaprice()
    return instaprice.crew().kickoff(inputs=inputs)

def main():
    """Função principal melhorada com ESPIONAGEM DE AGENTES 🕵️"""
    
    print("🤖 INSTAPRICE - Sistema Inteligente de Análise de Notas Fiscais")
    print("🕵️ VERSÃO COM INTERCEPTAÇÃO DE CONVERSAS DOS AGENTES")
    print("="*60)
    
    # Configura logger
    logger = setup_logger()
    log_execution_step(logger, "Iniciando sistema Instaprice com espionagem ativada")
    
    try:
        # Valida ambiente
        if not validate_environment():
            logger.error("Falha na validação do ambiente. Abortando execução.")
            sys.exit(1)
        
        # Verifica arquivo ZIP (caminho absoluto)
        caminho_zip = os.path.abspath(os.path.join(os.path.dirname(__file__), "202401_NFs.zip"))
        if not os.path.exists(caminho_zip):
            logger.error(f"❌ Arquivo ZIP não encontrado: {caminho_zip}")
            sys.exit(1)
        
        log_execution_step(logger, f"Arquivo ZIP encontrado: {caminho_zip}")
        
        # Pergunta do usuário (pode ser parametrizada)
        pergunta = os.getenv('PERGUNTA_USUARIO', 
                           "Realize uma análise comparativa dos maiores compradores e vendedores."
                           )
        
        # Diretório de dados (caminho absoluto)
        diretorio_dados = os.path.abspath(os.path.join(os.path.dirname(__file__), 'dados', 'notasfiscais'))
        os.makedirs(diretorio_dados, exist_ok=True)
        
        # Prepara inputs com caminhos absolutos
        inputs = {
            'caminho_zip': caminho_zip,
            'pergunta_usuario': pergunta,
            'diretorio_dados': diretorio_dados
        }
        
        log_execution_step(logger, f"Pergunta a ser processada: {pergunta}")
        
        # 🕵️ ATIVA ESPIONAGEM DOS AGENTES 🕵️
        log_execution_step(logger, "🎧 Iniciando interceptação das conversas dos agentes...")
        print("🎧 Iniciando interceptação das conversas dos agentes...")
        
        # Executa Instaprice com interceptação ativa
        result, pdf_espionagem = interceptar_conversas_instaprice(executar_instaprice_com_analise, inputs)
        
        # Loga resultado
        log_execution_step(logger, "Análise concluída com sucesso")
        logger.info(f"📋 Resultado: {result}")
        
        # Loga arquivo de espionagem
        log_execution_step(logger, f"🕵️ Relatório de espionagem gerado: {pdf_espionagem}")
        
        # Verifica se arquivo de sugestões foi criado
        arquivo_sugestoes = "sugestoes_instaprice.md"
        if os.path.exists(arquivo_sugestoes):
            log_execution_step(logger, f"Sugestões salvas em: {arquivo_sugestoes}")
        
        print("\n✅ Execução concluída com sucesso!")
        print(f"📋 Resultado: {result}")
        print(f"📁 Verifique os dados processados em: {diretorio_dados}")
        print(f"💡 Sugestões disponíveis em: {arquivo_sugestoes}")
        print(f"🕵️ RELATÓRIO DE ESPIONAGEM: {pdf_espionagem}")
        print("🔒 Documento confidencial contém todas as conversas interceptadas!")
        
    except KeyboardInterrupt:
        log_execution_step(logger, "Execução interrompida pelo usuário")
        print("\n⚠️ Execução interrompida pelo usuário")
    except Exception as e:
        log_error_with_context(logger, e, "Execução principal do Instaprice")
        print(f"\n❌ Erro durante execução: {str(e)}")
        print("🔍 Verifique os logs em logs/ para mais detalhes")
        sys.exit(1)

if __name__ == "__main__":
    main()