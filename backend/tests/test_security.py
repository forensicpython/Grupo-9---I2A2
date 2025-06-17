"""
Testes de segurança para o sistema Instaprice.
"""
import pytest
import tempfile
import os
from pathlib import Path
import pandas as pd

from utils.input_validator import InputValidator
from utils.exceptions import SecurityError, DataValidationError, FileProcessingError
from config.settings import InstapriceSettings


class TestInputValidator:
    """Testes para o validador de entrada."""
    
    def test_safe_filename_validation(self):
        """Testa validação de nomes de arquivo seguros."""
        # Nomes seguros
        assert InputValidator.validate_filename("dados.csv")
        assert InputValidator.validate_filename("notas_fiscais.zip")
        assert InputValidator.validate_filename("arquivo-teste_01.txt")
        
    def test_dangerous_filename_rejection(self):
        """Testa rejeição de nomes de arquivo perigosos."""
        dangerous_names = [
            "../../../etc/passwd",
            "arquivo.exe",
            "script.bat",
            "malware.sh",
            "arquivo<script>.csv",
            "teste|pipe.csv"
        ]
        
        for name in dangerous_names:
            with pytest.raises(SecurityError):
                InputValidator.validate_filename(name)
    
    def test_cnpj_validation(self):
        """Testa validação de CNPJ."""
        # CNPJs válidos
        assert InputValidator.validate_cnpj("12345678000190")
        assert InputValidator.validate_cnpj("12.345.678/0001-90")
        
        # CNPJs inválidos
        with pytest.raises(DataValidationError):
            InputValidator.validate_cnpj("123456780001")  # Muito curto
        
        with pytest.raises(DataValidationError):
            InputValidator.validate_cnpj("11111111111111")  # Todos iguais
    
    def test_query_injection_prevention(self):
        """Testa prevenção de injeção em consultas."""
        # Consultas seguras
        assert InputValidator.validate_query_string("Quais são os maiores compradores?")
        assert InputValidator.validate_query_string("Análise de vendedores por região")
        
        # Consultas perigosas
        dangerous_queries = [
            "DROP TABLE usuarios",
            "SELECT * FROM dados; DELETE FROM logs--",
            "UNION SELECT password FROM users",
            "<script>alert('xss')</script>",
            "'; EXEC sp_configure 'xp_cmdshell'",
        ]
        
        for query in dangerous_queries:
            with pytest.raises(SecurityError):
                InputValidator.validate_query_string(query)
    
    def test_file_size_validation(self):
        """Testa validação de tamanho de arquivo."""
        with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as f:
            # Cria arquivo pequeno (seguro)
            f.write(b"test data" * 100)
            f.flush()
            
            # Deve passar na validação
            assert InputValidator.validate_file_size(f.name)
            
            # Limpa
            os.unlink(f.name)
    
    def test_file_integrity_validation(self):
        """Testa validação de integridade de arquivo."""
        with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as f:
            test_data = b"col1,col2\nval1,val2\n"
            f.write(test_data)
            f.flush()
            
            # Testa validação completa
            result = InputValidator.validate_file_integrity(f.name)
            
            assert result.is_valid
            assert result.file_size == len(test_data)
            assert result.file_hash  # Hash deve existir
            
            # Limpa
            os.unlink(f.name)
    
    def test_input_sanitization(self):
        """Testa sanitização de entrada."""
        # Entradas com caracteres perigosos
        dirty_input = "Análise\x00com\x1fcaracteres\x7fde\x9fcontrole"
        clean_input = InputValidator.sanitize_user_input(dirty_input)
        
        assert "\x00" not in clean_input
        assert "\x1f" not in clean_input
        assert "\x7f" not in clean_input
        assert "\x9f" not in clean_input
        
        # Teste de tamanho
        long_input = "a" * 2000
        sanitized = InputValidator.sanitize_user_input(long_input)
        assert len(sanitized) <= 1000


class TestInstapriceSettings:
    """Testes para configurações do sistema."""
    
    def test_api_key_validation(self):
        """Testa validação de chaves de API."""
        # Chave válida
        valid_settings = InstapriceSettings(
            groq_api_key="gsk_" + "a" * 50,
            model_name="llama-3.1-8b-instant"
        )
        assert valid_settings.groq_api_key
        
        # Chave inválida
        with pytest.raises(ValueError):
            InstapriceSettings(
                groq_api_key="invalid_key",
                model_name="llama-3.1-8b-instant"
            )
    
    def test_model_validation(self):
        """Testa validação de modelos."""
        # Modelo válido
        valid_settings = InstapriceSettings(
            groq_api_key="gsk_" + "a" * 50,
            model_name="llama-3.1-8b-instant"
        )
        assert valid_settings.model_name == "llama-3.1-8b-instant"
        
        # Modelo inválido
        with pytest.raises(ValueError):
            InstapriceSettings(
                groq_api_key="gsk_" + "a" * 50,
                model_name="modelo_inexistente"
            )
    
    def test_parameter_ranges(self):
        """Testa validação de ranges de parâmetros."""
        # Parâmetros válidos
        valid_settings = InstapriceSettings(
            groq_api_key="gsk_" + "a" * 50,
            model_name="llama-3.1-8b-instant",
            max_tokens=2000,
            temperature=0.5,
            max_workers=4
        )
        
        assert 100 <= valid_settings.max_tokens <= 8000
        assert 0.0 <= valid_settings.temperature <= 2.0
        assert 1 <= valid_settings.max_workers <= 16


class TestSecurityMeasures:
    """Testes para medidas de segurança gerais."""
    
    def test_no_code_injection_in_pandas_operations(self):
        """Testa que operações pandas não permitem injeção de código."""
        # Simula DataFrame com dados suspeitos
        dangerous_data = {
            'empresa': ['EMPRESA A', '__import__("os").system("rm -rf /")'],
            'valor': [1000, 2000]
        }
        
        df = pd.DataFrame(dangerous_data)
        
        # Operações normais devem funcionar sem executar código
        result = df.groupby('empresa')['valor'].sum()
        
        # Verifica que o resultado é seguro
        assert len(result) == 2
        assert '__import__' in result.index  # String literal, não código executado
    
    def test_path_traversal_prevention(self):
        """Testa prevenção de path traversal."""
        dangerous_paths = [
            "../../../etc/passwd",
            "..\\..\\windows\\system32\\config",
            "/etc/shadow",
            "C:\\Windows\\System32\\config\\sam"
        ]
        
        for path in dangerous_paths:
            with pytest.raises(SecurityError):
                InputValidator.validate_file_path(path)
    
    def test_file_extension_whitelist(self):
        """Testa whitelist de extensões de arquivo."""
        # Extensões permitidas
        safe_extensions = ['.csv', '.zip', '.txt', '.json']
        for ext in safe_extensions:
            filename = f"teste{ext}"
            assert InputValidator.validate_filename(filename)
        
        # Extensões perigosas
        dangerous_extensions = ['.exe', '.bat', '.sh', '.ps1', '.cmd']
        for ext in dangerous_extensions:
            filename = f"teste{ext}"
            with pytest.raises(SecurityError):
                InputValidator.validate_filename(filename)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])