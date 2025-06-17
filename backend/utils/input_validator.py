"""
Validador robusto de entrada para prevenir ataques e garantir integridade dos dados.
"""
import re
import os
import hashlib
from pathlib import Path
from typing import Union, List, Optional, Tuple
from pydantic import BaseModel, Field, validator
from utils.exceptions import SecurityError, DataValidationError, FileProcessingError


class FileValidationResult(BaseModel):
    """Resultado da validação de arquivo."""
    is_valid: bool
    file_path: str
    file_size: int
    file_hash: str
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)


class InputValidator:
    """Validador robusto de entrada."""
    
    # Padrões de segurança
    SAFE_FILENAME_PATTERN = re.compile(r'^[a-zA-Z0-9_.-]+$')
    SAFE_PATH_PATTERN = re.compile(r'^[a-zA-Z0-9_/.-]+$')
    CNPJ_PATTERN = re.compile(r'^\d{14}$')
    
    # Extensões permitidas
    ALLOWED_EXTENSIONS = {'.zip', '.csv', '.txt', '.json'}
    
    # Tamanhos máximos (em bytes)
    MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
    MAX_ZIP_SIZE = 500 * 1024 * 1024   # 500MB
    
    # Padrões perigosos
    DANGEROUS_PATTERNS = [
        r'\.\./',          # Path traversal
        r'\.\.\\',         # Path traversal (Windows)
        r'[<>:"|?*]',      # Caracteres inválidos
        r'(javascript|script|vbscript):', # Scripts
        r'(data|javascript):', # Data URLs
        r'\.exe$',         # Executáveis
        r'\.bat$',         # Batch files
        r'\.cmd$',         # Command files
        r'\.sh$',          # Shell scripts
        r'\.ps1$',         # PowerShell
    ]
    
    @classmethod
    def validate_file_path(cls, file_path: Union[str, Path]) -> bool:
        """
        Valida se um caminho de arquivo é seguro.
        
        Args:
            file_path: Caminho do arquivo
            
        Returns:
            True se o caminho é seguro
            
        Raises:
            SecurityError: Se o caminho é perigoso
        """
        path_str = str(file_path)
        
        # Verifica padrões perigosos
        for pattern in cls.DANGEROUS_PATTERNS:
            if re.search(pattern, path_str, re.IGNORECASE):
                raise SecurityError(
                    f"Caminho de arquivo contém padrão perigoso: {pattern}",
                    security_level="HIGH",
                    file_path=path_str
                )
        
        # Verifica se é um caminho absoluto válido
        try:
            resolved_path = Path(path_str).resolve()
            if not cls.SAFE_PATH_PATTERN.match(str(resolved_path)):
                raise SecurityError(
                    "Caminho de arquivo contém caracteres inválidos",
                    file_path=path_str
                )
        except Exception as e:
            raise SecurityError(
                f"Caminho de arquivo inválido: {e}",
                file_path=path_str
            )
        
        return True
    
    @classmethod
    def validate_filename(cls, filename: str) -> bool:
        """
        Valida se um nome de arquivo é seguro.
        
        Args:
            filename: Nome do arquivo
            
        Returns:
            True se o nome é seguro
            
        Raises:
            SecurityError: Se o nome é perigoso
        """
        if not cls.SAFE_FILENAME_PATTERN.match(filename):
            raise SecurityError(
                "Nome de arquivo contém caracteres inválidos",
                filename=filename
            )
        
        # Verifica extensão
        extension = Path(filename).suffix.lower()
        if extension not in cls.ALLOWED_EXTENSIONS:
            raise SecurityError(
                f"Extensão de arquivo não permitida: {extension}",
                filename=filename,
                allowed_extensions=list(cls.ALLOWED_EXTENSIONS)
            )
        
        return True
    
    @classmethod
    def validate_file_size(cls, file_path: Union[str, Path]) -> bool:
        """
        Valida o tamanho de um arquivo.
        
        Args:
            file_path: Caminho do arquivo
            
        Returns:
            True se o tamanho é válido
            
        Raises:
            FileProcessingError: Se o arquivo é muito grande
        """
        try:
            file_size = os.path.getsize(file_path)
            
            # Determina limite baseado na extensão
            extension = Path(file_path).suffix.lower()
            max_size = cls.MAX_ZIP_SIZE if extension == '.zip' else cls.MAX_FILE_SIZE
            
            if file_size > max_size:
                raise FileProcessingError(
                    f"Arquivo muito grande: {file_size} bytes (máximo: {max_size})",
                    file_path=str(file_path),
                    file_size=file_size
                )
            
            return True
            
        except OSError as e:
            raise FileProcessingError(
                f"Erro ao verificar tamanho do arquivo: {e}",
                file_path=str(file_path)
            )
    
    @classmethod
    def calculate_file_hash(cls, file_path: Union[str, Path]) -> str:
        """
        Calcula hash SHA-256 de um arquivo.
        
        Args:
            file_path: Caminho do arquivo
            
        Returns:
            Hash SHA-256 do arquivo
        """
        hash_sha256 = hashlib.sha256()
        
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
            
        except Exception as e:
            raise FileProcessingError(
                f"Erro ao calcular hash do arquivo: {e}",
                file_path=str(file_path)
            )
    
    @classmethod
    def validate_file_integrity(cls, file_path: Union[str, Path], 
                              expected_hash: Optional[str] = None) -> FileValidationResult:
        """
        Valida completamente um arquivo.
        
        Args:
            file_path: Caminho do arquivo
            expected_hash: Hash esperado (opcional)
            
        Returns:
            Resultado da validação
        """
        errors = []
        warnings = []
        
        # Converte para Path
        path = Path(file_path)
        
        # Verifica se arquivo existe
        if not path.exists():
            errors.append(f"Arquivo não encontrado: {file_path}")
            return FileValidationResult(
                is_valid=False,
                file_path=str(file_path),
                file_size=0,
                file_hash="",
                errors=errors
            )
        
        # Validações de segurança
        try:
            cls.validate_file_path(file_path)
            cls.validate_filename(path.name)
            cls.validate_file_size(file_path)
        except (SecurityError, FileProcessingError) as e:
            errors.append(str(e))
        
        # Calcula informações do arquivo
        try:
            file_size = path.stat().st_size
            file_hash = cls.calculate_file_hash(file_path)
        except Exception as e:
            errors.append(f"Erro ao acessar arquivo: {e}")
            file_size = 0
            file_hash = ""
        
        # Verifica hash se fornecido
        if expected_hash and file_hash:
            if file_hash != expected_hash:
                errors.append(f"Hash do arquivo não confere. Esperado: {expected_hash}, Atual: {file_hash}")
        
        # Verificações adicionais por tipo
        if path.suffix.lower() == '.zip':
            if file_size > cls.MAX_ZIP_SIZE:
                warnings.append("Arquivo ZIP muito grande, processamento pode ser lento")
        
        return FileValidationResult(
            is_valid=len(errors) == 0,
            file_path=str(file_path),
            file_size=file_size,
            file_hash=file_hash,
            errors=errors,
            warnings=warnings
        )
    
    @classmethod
    def validate_cnpj(cls, cnpj: str) -> bool:
        """
        Valida formato de CNPJ.
        
        Args:
            cnpj: CNPJ a ser validado
            
        Returns:
            True se válido
            
        Raises:
            DataValidationError: Se CNPJ é inválido
        """
        # Remove caracteres não numéricos
        cnpj_clean = re.sub(r'[^\d]', '', cnpj)
        
        # Verifica se tem 14 dígitos
        if not cls.CNPJ_PATTERN.match(cnpj_clean):
            raise DataValidationError(
                "CNPJ deve ter 14 dígitos numéricos",
                context={"cnpj": cnpj, "cnpj_clean": cnpj_clean}
            )
        
        # Verifica se não são todos iguais
        if len(set(cnpj_clean)) == 1:
            raise DataValidationError(
                "CNPJ não pode ter todos os dígitos iguais",
                context={"cnpj": cnpj}
            )
        
        return True
    
    @classmethod
    def validate_query_string(cls, query: str) -> bool:
        """
        Valida string de consulta para prevenir injeções.
        
        Args:
            query: String de consulta
            
        Returns:
            True se válida
            
        Raises:
            SecurityError: Se contém padrões perigosos
        """
        if not query or len(query) > 1000:
            raise DataValidationError(
                "Consulta deve ter entre 1 e 1000 caracteres",
                context={"query_length": len(query) if query else 0}
            )
        
        # Padrões SQL perigosos (básico)
        dangerous_sql = [
            r'(drop|delete|truncate|alter)\s+table',
            r'(insert|update)\s+.*\s+set',
            r'union\s+select',
            r'--',
            r'/\*.*\*/',
            r'(exec|execute)\s*\(',
            r'(script|javascript)',
            r'<script',
        ]
        
        query_lower = query.lower()
        for pattern in dangerous_sql:
            if re.search(pattern, query_lower):
                raise SecurityError(
                    f"Consulta contém padrão perigoso: {pattern}",
                    security_level="HIGH",
                    query=query[:100] + "..." if len(query) > 100 else query
                )
        
        return True
    
    @classmethod
    def sanitize_user_input(cls, user_input: str) -> str:
        """
        Sanitiza entrada do usuário.
        
        Args:
            user_input: Entrada do usuário
            
        Returns:
            Entrada sanitizada
        """
        if not user_input:
            return ""
        
        # Remove caracteres de controle
        sanitized = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', user_input)
        
        # Limita tamanho
        if len(sanitized) > 1000:
            sanitized = sanitized[:1000]
        
        # Remove múltiplos espaços
        sanitized = re.sub(r'\s+', ' ', sanitized).strip()
        
        return sanitized