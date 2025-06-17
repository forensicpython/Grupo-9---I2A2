"""
Exceções personalizadas para o sistema Instaprice.
Fornece tratamento específico e contextualizado de erros.
"""
from typing import Optional, Dict, Any


class InstapriceException(Exception):
    """Exceção base do sistema Instaprice."""
    
    def __init__(self, message: str, error_code: Optional[str] = None, context: Optional[Dict[str, Any]] = None):
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        self.context = context or {}
        super().__init__(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte exceção para dicionário."""
        return {
            "error_type": self.__class__.__name__,
            "error_code": self.error_code,
            "message": self.message,
            "context": self.context
        }


class ConfigurationError(InstapriceException):
    """Erro de configuração do sistema."""
    pass


class DataValidationError(InstapriceException):
    """Erro de validação de dados."""
    
    def __init__(self, message: str, invalid_records: Optional[int] = None, 
                 validation_errors: Optional[list] = None, **kwargs):
        self.invalid_records = invalid_records
        self.validation_errors = validation_errors or []
        
        context = {
            "invalid_records": invalid_records,
            "validation_errors_count": len(self.validation_errors),
            **kwargs
        }
        
        super().__init__(message, context=context)


class FileProcessingError(InstapriceException):
    """Erro de processamento de arquivos."""
    
    def __init__(self, message: str, file_path: Optional[str] = None, 
                 file_size: Optional[int] = None, **kwargs):
        self.file_path = file_path
        self.file_size = file_size
        
        context = {
            "file_path": file_path,
            "file_size": file_size,
            **kwargs
        }
        
        super().__init__(message, context=context)


class ExtractionError(FileProcessingError):
    """Erro específico de extração de arquivos."""
    pass


class CSVProcessingError(FileProcessingError):
    """Erro específico de processamento de CSV."""
    
    def __init__(self, message: str, csv_file: Optional[str] = None, 
                 row_number: Optional[int] = None, **kwargs):
        self.csv_file = csv_file
        self.row_number = row_number
        
        context = {
            "csv_file": csv_file,
            "row_number": row_number,
            **kwargs
        }
        
        super().__init__(message, context=context)


class LLMApiError(InstapriceException):
    """Erro de API do LLM."""
    
    def __init__(self, message: str, api_response_code: Optional[int] = None,
                 model_name: Optional[str] = None, **kwargs):
        self.api_response_code = api_response_code
        self.model_name = model_name
        
        context = {
            "api_response_code": api_response_code,
            "model_name": model_name,
            **kwargs
        }
        
        super().__init__(message, context=context)


class AgentExecutionError(InstapriceException):
    """Erro de execução de agente."""
    
    def __init__(self, message: str, agent_name: Optional[str] = None,
                 task_name: Optional[str] = None, **kwargs):
        self.agent_name = agent_name
        self.task_name = task_name
        
        context = {
            "agent_name": agent_name,
            "task_name": task_name,
            **kwargs
        }
        
        super().__init__(message, context=context)


class SecurityError(InstapriceException):
    """Erro de segurança."""
    
    def __init__(self, message: str, security_level: str = "HIGH", **kwargs):
        self.security_level = security_level
        
        context = {
            "security_level": security_level,
            **kwargs
        }
        
        super().__init__(message, context=context)


class RateLimitError(InstapriceException):
    """Erro de limite de taxa."""
    
    def __init__(self, message: str, retry_after: Optional[int] = None, **kwargs):
        self.retry_after = retry_after
        
        context = {
            "retry_after": retry_after,
            **kwargs
        }
        
        super().__init__(message, context=context)


class TimeoutError(InstapriceException):
    """Erro de timeout."""
    
    def __init__(self, message: str, timeout_seconds: Optional[int] = None, **kwargs):
        self.timeout_seconds = timeout_seconds
        
        context = {
            "timeout_seconds": timeout_seconds,
            **kwargs
        }
        
        super().__init__(message, context=context)


class DataIntegrityError(InstapriceException):
    """Erro de integridade de dados."""
    
    def __init__(self, message: str, expected_checksum: Optional[str] = None,
                 actual_checksum: Optional[str] = None, **kwargs):
        self.expected_checksum = expected_checksum
        self.actual_checksum = actual_checksum
        
        context = {
            "expected_checksum": expected_checksum,
            "actual_checksum": actual_checksum,
            **kwargs
        }
        
        super().__init__(message, context=context)


# Decorador para tratamento automático de exceções
def handle_exceptions(exception_mapping: Optional[Dict[type, type]] = None):
    """
    Decorador para tratamento automático de exceções.
    
    Args:
        exception_mapping: Mapeamento de exceções padrão para exceções customizadas
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # Se é uma exceção customizada, apenas re-raise
                if isinstance(e, InstapriceException):
                    raise
                
                # Mapeia exceções conhecidas
                if exception_mapping:
                    for original_exc, custom_exc in exception_mapping.items():
                        if isinstance(e, original_exc):
                            raise custom_exc(
                                f"Error in {func.__name__}: {str(e)}",
                                context={"original_exception": type(e).__name__}
                            ) from e
                
                # Exceção genérica para casos não mapeados
                raise InstapriceException(
                    f"Unexpected error in {func.__name__}: {str(e)}",
                    context={"original_exception": type(e).__name__}
                ) from e
        
        return wrapper
    return decorator


# Mapeamentos comuns de exceções
COMMON_EXCEPTION_MAPPING = {
    FileNotFoundError: FileProcessingError,
    PermissionError: SecurityError,
    ValueError: DataValidationError,
    KeyError: DataValidationError,
    ConnectionError: LLMApiError,
    TimeoutError: TimeoutError,
}


def get_user_friendly_message(exception: Exception) -> str:
    """
    Retorna uma mensagem amigável para o usuário baseada na exceção.
    
    Args:
        exception: Exceção a ser traduzida
        
    Returns:
        Mensagem amigável para o usuário
    """
    if isinstance(exception, ConfigurationError):
        return "❌ Erro de configuração. Verifique suas configurações e tente novamente."
    
    elif isinstance(exception, DataValidationError):
        return f"❌ Erro na validação dos dados. {exception.invalid_records or 'Alguns'} registros inválidos encontrados."
    
    elif isinstance(exception, FileProcessingError):
        return f"❌ Erro ao processar arquivo. Verifique se o arquivo está correto e acessível."
    
    elif isinstance(exception, LLMApiError):
        return "❌ Erro na comunicação com o serviço de IA. Tente novamente em alguns minutos."
    
    elif isinstance(exception, SecurityError):
        return "❌ Erro de segurança detectado. Operação bloqueada."
    
    elif isinstance(exception, TimeoutError):
        return "⏱️ Operação demorou mais que o esperado. Tente novamente."
    
    elif isinstance(exception, RateLimitError):
        retry_msg = f" Tente novamente em {exception.retry_after} segundos." if exception.retry_after else ""
        return f"⚠️ Limite de uso atingido.{retry_msg}"
    
    else:
        return "❌ Erro inesperado. Contate o suporte se o problema persistir."