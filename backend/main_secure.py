#!/usr/bin/env python3
"""
Instaprice - Sistema Inteligente de Análise de Notas Fiscais
Versão Segura e Otimizada - SEM sistema de espionagem
"""

import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional

# Adiciona o diretório atual ao path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Imports locais
from instaprice import Instaprice
from config.settings import get_settings, validate_startup_config
from utils.secure_logger import get_secure_logger, AuditEventType
from utils.exceptions import (
    InstapriceException, ConfigurationError, FileProcessingError,
    get_user_friendly_message, handle_exceptions, COMMON_EXCEPTION_MAPPING
)
from utils.input_validator import InputValidator

# Configurações e logger
settings = get_settings()
logger = get_secure_logger("instaprice_main")


@handle_exceptions(COMMON_EXCEPTION_MAPPING)
def validate_environment() -> bool:
    """Valida configuração do ambiente de forma robusta."""
    try:
        # Valida configurações do sistema
        if not validate_startup_config():
            raise ConfigurationError("Falha na validação das configurações do sistema")
        
        # Valida API key
        if not settings.groq_api_key or settings.groq_api_key == 'your_groq_api_key_here':
            raise ConfigurationError(
                "GROQ_API_KEY não configurada. Configure uma chave válida no arquivo .env"
            )
        
        logger.info("Configurações validadas com sucesso", 
                   model=settings.model_name, 
                   max_tokens=settings.max_tokens)
        
        return True
        
    except Exception as e:
        logger.error("Falha na validação do ambiente", exception=e)
        raise


@handle_exceptions(COMMON_EXCEPTION_MAPPING)
def validate_input_files(caminho_zip: str, diretorio_dados: str) -> Dict[str, Any]:
    """Valida arquivos de entrada de forma segura."""
    logger.audit(AuditEventType.FILE_ACCESS, "Validating input files", 
                zip_path=caminho_zip, data_dir=diretorio_dados)
    
    # Valida arquivo ZIP
    if not os.path.exists(caminho_zip):
        raise FileProcessingError(
            f"Arquivo ZIP não encontrado: {caminho_zip}",
            file_path=caminho_zip
        )
    
    # Validação de segurança do arquivo
    validation_result = InputValidator.validate_file_integrity(caminho_zip)
    if not validation_result.is_valid:
        raise FileProcessingError(
            f"Arquivo ZIP inválido: {'; '.join(validation_result.errors)}",
            file_path=caminho_zip,
            file_size=validation_result.file_size
        )
    
    # Cria diretório de dados se não existir
    os.makedirs(diretorio_dados, exist_ok=True)
    
    logger.info("Arquivos de entrada validados", 
               zip_size=validation_result.file_size,
               zip_hash=validation_result.file_hash[:16])
    
    return {
        'zip_size': validation_result.file_size,
        'zip_hash': validation_result.file_hash,
        'warnings': validation_result.warnings
    }


@handle_exceptions(COMMON_EXCEPTION_MAPPING)
def execute_instaprice_analysis(inputs: Dict[str, Any]) -> str:
    """Executa análise do Instaprice de forma segura."""
    logger.audit(AuditEventType.SYSTEM_START, "Starting Instaprice analysis")
    
    try:
        # Valida entrada da consulta
        pergunta = inputs.get('pergunta_usuario', '')
        InputValidator.validate_query_string(pergunta)
        
        # Cria instância do Instaprice
        instaprice = Instaprice()
        
        # Executa análise
        logger.execution_step("Iniciando crew do Instaprice")
        result = instaprice.crew().kickoff(inputs=inputs)
        
        logger.audit(AuditEventType.SYSTEM_STOP, "Instaprice analysis completed successfully")
        return result
        
    except Exception as e:
        logger.error("Erro durante execução do Instaprice", exception=e)
        raise


def main():
    """Função principal segura e otimizada."""
    
    print("🤖 INSTAPRICE - Sistema Inteligente de Análise de Notas Fiscais")
    print("🔒 VERSÃO SEGURA E OTIMIZADA")
    print("="*60)
    
    try:
        # Inicializa logger
        logger.audit(AuditEventType.SYSTEM_START, "Instaprice system starting")
        
        # 1. Valida ambiente
        logger.execution_step("Validando ambiente")
        validate_environment()
        
        # 2. Configura caminhos
        caminho_zip = os.path.abspath(os.path.join(os.path.dirname(__file__), "202401_NFs.zip"))
        diretorio_dados = settings.get_data_directory()
        
        # 3. Valida arquivos de entrada
        logger.execution_step("Validando arquivos de entrada")
        file_info = validate_input_files(str(caminho_zip), str(diretorio_dados))
        
        # Exibe warnings se houver
        for warning in file_info.get('warnings', []):
            print(f"⚠️ {warning}")
        
        # 4. Prepara dados de entrada
        pergunta = settings.pergunta_usuario
        
        # Sanitiza entrada do usuário
        pergunta_sanitizada = InputValidator.sanitize_user_input(pergunta)
        
        inputs = {
            'caminho_zip': str(caminho_zip),
            'pergunta_usuario': pergunta_sanitizada,
            'diretorio_dados': str(diretorio_dados)
        }
        
        logger.info("Iniciando análise", 
                   pergunta=pergunta_sanitizada[:100],
                   zip_size=file_info['zip_size'])
        
        print(f"\n📋 Pergunta: {pergunta_sanitizada}")
        print(f"📁 Arquivo ZIP: {caminho_zip}")
        print(f"📊 Tamanho: {file_info['zip_size']:,} bytes")
        print(f"🎯 Diretório de dados: {diretorio_dados}")
        print("\n🚀 Iniciando análise...")
        
        # 5. Executa análise principal
        logger.execution_step("Executando análise principal")
        result = execute_instaprice_analysis(inputs)
        
        # 6. Apresenta resultados
        print("\n✅ Análise concluída com sucesso!")
        print(f"📋 Resultado:\n{result}")
        
        # Verifica arquivo de sugestões
        arquivo_sugestoes = "sugestoes_instaprice.md"
        if os.path.exists(arquivo_sugestoes):
            print(f"💡 Sugestões salvas em: {arquivo_sugestoes}")
        
        print(f"📁 Dados processados em: {diretorio_dados}")
        print("🔒 Análise executada com segurança e auditoria completa")
        
        logger.audit(AuditEventType.SYSTEM_STOP, "Instaprice system completed successfully")
        
    except KeyboardInterrupt:
        logger.info("Execução interrompida pelo usuário")
        print("\n⚠️ Execução interrompida pelo usuário")
        sys.exit(1)
        
    except InstapriceException as e:
        # Exceções conhecidas do sistema
        user_message = get_user_friendly_message(e)
        logger.error("Erro conhecido do sistema", exception=e)
        print(f"\n{user_message}")
        print(f"🔍 Código do erro: {e.error_code}")
        
        # Log detalhado para debug
        if settings.log_level == "DEBUG":
            print(f"📋 Contexto: {e.context}")
        
        sys.exit(1)
        
    except Exception as e:
        # Exceções não tratadas
        logger.error("Erro inesperado", exception=e)
        print(f"\n❌ Erro inesperado: {str(e)}")
        print("🔍 Verifique os logs para mais detalhes")
        print(f"📁 Logs em: {settings.get_logs_directory()}")
        sys.exit(1)


if __name__ == "__main__":
    main()