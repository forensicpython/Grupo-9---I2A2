"""
Configurações centralizadas do sistema Instaprice com validação robusta.
"""
from pydantic import BaseSettings, Field, validator
from typing import Optional
import os
from pathlib import Path

class InstapriceSettings(BaseSettings):
    """Configurações do sistema Instaprice com validação automática."""
    
    # API Configuration
    groq_api_key: str = Field(..., description="Chave da API Groq (obrigatória)")
    model_name: str = Field(default="llama-3.1-8b-instant", description="Nome do modelo LLM")
    max_tokens: int = Field(default=3000, ge=100, le=8000, description="Máximo de tokens")
    temperature: float = Field(default=0.1, ge=0.0, le=2.0, description="Temperatura do modelo")
    
    # System Configuration
    max_workers: int = Field(default=4, ge=1, le=16, description="Máximo de workers")
    cache_size: int = Field(default=10, ge=1, le=100, description="Tamanho do cache")
    timeout_seconds: int = Field(default=300, ge=30, le=3600, description="Timeout em segundos")
    
    # File Configuration
    max_file_size_mb: int = Field(default=100, ge=1, le=1000, description="Tamanho máximo de arquivo em MB")
    allowed_extensions: list = Field(default=[".zip", ".csv"], description="Extensões permitidas")
    
    # Logging Configuration
    log_level: str = Field(default="INFO", description="Nível de log")
    log_format: str = Field(default="json", description="Formato do log")
    
    # Security Configuration
    enable_audit: bool = Field(default=True, description="Habilitar auditoria")
    max_retries: int = Field(default=3, ge=1, le=10, description="Máximo de tentativas")
    
    # Default Question
    pergunta_usuario: str = Field(
        default="Realize uma análise comparativa dos maiores compradores e vendedores",
        description="Pergunta padrão do usuário"
    )
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        
    @validator('groq_api_key')
    def validate_api_key(cls, v):
        """Valida se a API key não é um placeholder."""
        if not v or v in ['your_groq_api_key_here', 'placeholder', '']:
            raise ValueError("GROQ_API_KEY deve ser configurada com uma chave válida")
        if len(v) < 20:
            raise ValueError("GROQ_API_KEY parece ser inválida (muito curta)")
        return v
    
    @validator('model_name')
    def validate_model_name(cls, v):
        """Valida o nome do modelo."""
        allowed_models = [
            "llama-3.1-8b-instant",
            "llama-3.3-70b-versatile", 
            "llama3-8b-8192",
            "llama3-70b-8192"
        ]
        if v not in allowed_models:
            raise ValueError(f"Modelo {v} não é suportado. Use: {allowed_models}")
        return v
    
    @validator('log_level')
    def validate_log_level(cls, v):
        """Valida o nível de log."""
        allowed_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in allowed_levels:
            raise ValueError(f"Log level deve ser um de: {allowed_levels}")
        return v.upper()
    
    def get_data_directory(self) -> Path:
        """Retorna o diretório de dados padrão."""
        return Path(__file__).parent.parent / "dados" / "notasfiscais"
    
    def get_logs_directory(self) -> Path:
        """Retorna o diretório de logs."""
        return Path(__file__).parent.parent / "logs"
    
    def validate_environment(self) -> bool:
        """Valida se o ambiente está configurado corretamente."""
        try:
            # Verifica se diretórios existem ou podem ser criados
            data_dir = self.get_data_directory()
            logs_dir = self.get_logs_directory()
            
            data_dir.mkdir(parents=True, exist_ok=True)
            logs_dir.mkdir(parents=True, exist_ok=True)
            
            return True
        except Exception as e:
            raise EnvironmentError(f"Erro na validação do ambiente: {e}")

# Instância global das configurações
settings = InstapriceSettings()

def get_settings() -> InstapriceSettings:
    """Retorna as configurações do sistema."""
    return settings

def validate_startup_config():
    """Valida configurações na inicialização do sistema."""
    try:
        settings.validate_environment()
        return True
    except Exception as e:
        print(f"❌ Erro na configuração: {e}")
        return False