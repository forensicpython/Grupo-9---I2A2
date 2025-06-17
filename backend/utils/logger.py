import logging
import os
from datetime import datetime
from pathlib import Path

def setup_logger(name: str = "instaprice", log_level: str = "INFO") -> logging.Logger:
    """
    Configura sistema de logging para o Instaprice
    
    Args:
        name: Nome do logger
        log_level: Nível de log (DEBUG, INFO, WARNING, ERROR)
    
    Returns:
        Logger configurado
    """
    
    # Cria diretório de logs se não existir
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Nome do arquivo de log com timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_dir / f"instaprice_{timestamp}.log"
    
    # Configuração do logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    
    # Remove handlers existentes para evitar duplicação
    logger.handlers.clear()
    
    # Handler para arquivo
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    
    # Handler para console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    
    # Formato das mensagens
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Adiciona handlers ao logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

def log_execution_step(logger: logging.Logger, step_name: str, agent_name: str = None):
    """
    Loga etapas de execução do sistema
    
    Args:
        logger: Logger configurado
        step_name: Nome da etapa
        agent_name: Nome do agente (opcional)
    """
    if agent_name:
        logger.info(f"🤖 [{agent_name}] {step_name}")
    else:
        logger.info(f"📋 {step_name}")

def log_error_with_context(logger: logging.Logger, error: Exception, context: str = ""):
    """
    Loga erros com contexto adicional
    
    Args:
        logger: Logger configurado
        error: Exceção capturada
        context: Contexto adicional do erro
    """
    error_msg = f"❌ ERRO: {str(error)}"
    if context:
        error_msg += f" | Contexto: {context}"
    
    logger.error(error_msg, exc_info=True)