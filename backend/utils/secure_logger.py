"""
Sistema de logging estruturado e seguro para o Instaprice.
Substitui o sistema de "espionagem" por auditoria adequada.
"""
import logging
import json
import uuid
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path
import hashlib
from enum import Enum

class LogLevel(Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

class AuditEventType(Enum):
    SYSTEM_START = "system_start"
    SYSTEM_STOP = "system_stop"
    DATA_PROCESSING = "data_processing"
    AGENT_EXECUTION = "agent_execution"
    API_CALL = "api_call"
    ERROR_OCCURRED = "error_occurred"
    DATA_VALIDATION = "data_validation"
    FILE_ACCESS = "file_access"

class SecureLogger:
    """Logger estruturado e seguro que substitui o sistema de espionagem."""
    
    def __init__(self, name: str, log_dir: Optional[Path] = None):
        self.name = name
        self.session_id = str(uuid.uuid4())
        self.log_dir = log_dir or Path(__file__).parent.parent / "logs"
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Configura loggers
        self._setup_loggers()
        
    def _setup_loggers(self):
        """Configura os loggers estruturados."""
        # Logger principal
        self.logger = logging.getLogger(self.name)
        self.logger.setLevel(logging.INFO)
        
        # Logger de auditoria
        self.audit_logger = logging.getLogger(f"{self.name}.audit")
        self.audit_logger.setLevel(logging.INFO)
        
        # Handler para arquivo principal
        main_handler = logging.FileHandler(
            self.log_dir / f"instaprice_{datetime.now().strftime('%Y%m%d')}.log"
        )
        main_handler.setFormatter(self._get_json_formatter())
        
        # Handler para auditoria
        audit_handler = logging.FileHandler(
            self.log_dir / f"audit_{datetime.now().strftime('%Y%m%d')}.log"
        )
        audit_handler.setFormatter(self._get_json_formatter())
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(self._get_console_formatter())
        
        # Adiciona handlers
        if not self.logger.handlers:
            self.logger.addHandler(main_handler)
            self.logger.addHandler(console_handler)
            
        if not self.audit_logger.handlers:
            self.audit_logger.addHandler(audit_handler)
    
    def _get_json_formatter(self):
        """Retorna formatter JSON estruturado."""
        return logging.Formatter(
            '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "message": %(message)s, "session_id": "' + self.session_id + '"}'
        )
    
    def _get_console_formatter(self):
        """Retorna formatter para console."""
        return logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    def _sanitize_data(self, data: Any) -> Any:
        """Remove dados sensíveis dos logs."""
        if isinstance(data, dict):
            sanitized = {}
            for key, value in data.items():
                if any(sensitive in key.lower() for sensitive in ['password', 'token', 'key', 'secret']):
                    sanitized[key] = "***REDACTED***"
                elif isinstance(value, (dict, list)):
                    sanitized[key] = self._sanitize_data(value)
                else:
                    sanitized[key] = value
            return sanitized
        elif isinstance(data, list):
            return [self._sanitize_data(item) for item in data]
        return data
    
    def _create_log_entry(self, level: LogLevel, message: str, **kwargs) -> Dict[str, Any]:
        """Cria entrada de log estruturada."""
        entry = {
            "message": message,
            "level": level.value,
            "timestamp": datetime.utcnow().isoformat(),
            "session_id": self.session_id,
        }
        
        # Adiciona dados extras sanitizados
        if kwargs:
            entry["data"] = self._sanitize_data(kwargs)
            
        return entry
    
    def info(self, message: str, **kwargs):
        """Log de informação."""
        entry = self._create_log_entry(LogLevel.INFO, message, **kwargs)
        self.logger.info(json.dumps(entry))
    
    def warning(self, message: str, **kwargs):
        """Log de warning."""
        entry = self._create_log_entry(LogLevel.WARNING, message, **kwargs)
        self.logger.warning(json.dumps(entry))
    
    def error(self, message: str, exception: Optional[Exception] = None, **kwargs):
        """Log de erro."""
        if exception:
            kwargs["exception"] = {
                "type": type(exception).__name__,
                "message": str(exception),
                "traceback_hash": hashlib.md5(str(exception).encode()).hexdigest()[:8]
            }
        
        entry = self._create_log_entry(LogLevel.ERROR, message, **kwargs)
        self.logger.error(json.dumps(entry))
    
    def debug(self, message: str, **kwargs):
        """Log de debug."""
        entry = self._create_log_entry(LogLevel.DEBUG, message, **kwargs)
        self.logger.debug(json.dumps(entry))
    
    def audit(self, event_type: AuditEventType, description: str, **kwargs):
        """Log de auditoria."""
        entry = {
            "event_type": event_type.value,
            "description": description,
            "timestamp": datetime.utcnow().isoformat(),
            "session_id": self.session_id,
            "data": self._sanitize_data(kwargs)
        }
        
        self.audit_logger.info(json.dumps(entry))
    
    def execution_step(self, step: str, **kwargs):
        """Log de passo de execução (substitui espionagem)."""
        self.audit(
            AuditEventType.AGENT_EXECUTION,
            f"Executing step: {step}",
            step=step,
            **kwargs
        )
    
    def data_processed(self, file_name: str, records_count: int, **kwargs):
        """Log de processamento de dados."""
        self.audit(
            AuditEventType.DATA_PROCESSING,
            f"Data processed: {file_name}",
            file_name=file_name,
            records_count=records_count,
            **kwargs
        )
    
    def api_call(self, service: str, status: str, duration_ms: float, **kwargs):
        """Log de chamada de API."""
        self.audit(
            AuditEventType.API_CALL,
            f"API call to {service}",
            service=service,
            status=status,
            duration_ms=duration_ms,
            **kwargs
        )

# Factory function para criar loggers
def get_secure_logger(name: str) -> SecureLogger:
    """Cria um logger seguro."""
    return SecureLogger(name)

# Instância global
secure_logger = get_secure_logger("instaprice")

# Funções de conveniência
def log_execution_step(step: str, **kwargs):
    """Log de passo de execução."""
    secure_logger.execution_step(step, **kwargs)

def log_error_with_context(exception: Exception, context: str, **kwargs):
    """Log de erro com contexto."""
    secure_logger.error(f"Error in {context}", exception=exception, **kwargs)

def log_data_processed(file_name: str, records_count: int, **kwargs):
    """Log de dados processados."""
    secure_logger.data_processed(file_name, records_count, **kwargs)