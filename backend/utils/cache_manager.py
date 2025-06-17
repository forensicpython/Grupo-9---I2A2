"""
Sistema de cache otimizado para melhorar performance do Instaprice.
"""
import hashlib
import pickle
import time
from pathlib import Path
from typing import Any, Optional, Dict, Callable, Union
from functools import wraps
import pandas as pd
from config.settings import get_settings

settings = get_settings()


class CacheManager:
    """Gerenciador de cache thread-safe."""
    
    def __init__(self, cache_dir: Optional[Path] = None, max_size: int = 50):
        self.cache_dir = cache_dir or (Path(__file__).parent.parent / "cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.max_size = max_size
        self.memory_cache: Dict[str, tuple] = {}  # {key: (data, timestamp)}
        
    def _generate_key(self, *args, **kwargs) -> str:
        """Gera chave única para os argumentos."""
        key_data = str(args) + str(sorted(kwargs.items()))
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def _is_expired(self, timestamp: float, ttl: int) -> bool:
        """Verifica se item do cache expirou."""
        return time.time() - timestamp > ttl
    
    def _cleanup_memory_cache(self):
        """Limpa cache em memória se necessário."""
        if len(self.memory_cache) > self.max_size:
            # Remove 20% dos itens mais antigos
            items_to_remove = len(self.memory_cache) // 5
            sorted_items = sorted(self.memory_cache.items(), 
                                key=lambda x: x[1][1])  # Sort by timestamp
            
            for key, _ in sorted_items[:items_to_remove]:
                del self.memory_cache[key]
    
    def get(self, key: str, ttl: int = 3600) -> Optional[Any]:
        """
        Recupera item do cache.
        
        Args:
            key: Chave do cache
            ttl: Time to live em segundos
            
        Returns:
            Dados do cache ou None se não encontrado/expirado
        """
        # Verifica cache em memória primeiro
        if key in self.memory_cache:
            data, timestamp = self.memory_cache[key]
            if not self._is_expired(timestamp, ttl):
                return data
            else:
                del self.memory_cache[key]
        
        # Verifica cache em disco
        cache_file = self.cache_dir / f"{key}.pkl"
        if cache_file.exists():
            try:
                file_age = time.time() - cache_file.stat().st_mtime
                if file_age < ttl:
                    with open(cache_file, 'rb') as f:
                        data = pickle.load(f)
                    
                    # Adiciona ao cache em memória
                    self.memory_cache[key] = (data, time.time())
                    return data
                else:
                    cache_file.unlink()  # Remove arquivo expirado
            except Exception:
                cache_file.unlink()  # Remove arquivo corrompido
        
        return None
    
    def set(self, key: str, data: Any):
        """
        Armazena item no cache.
        
        Args:
            key: Chave do cache
            data: Dados a serem armazenados
        """
        timestamp = time.time()
        
        # Armazena em memória
        self.memory_cache[key] = (data, timestamp)
        self._cleanup_memory_cache()
        
        # Armazena em disco (para DataFrames grandes)
        if isinstance(data, pd.DataFrame) or len(str(data)) > 10000:
            cache_file = self.cache_dir / f"{key}.pkl"
            try:
                with open(cache_file, 'wb') as f:
                    pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)
            except Exception:
                pass  # Se falhar, mantém apenas em memória
    
    def clear(self):
        """Limpa todo o cache."""
        self.memory_cache.clear()
        
        # Remove arquivos de cache
        for cache_file in self.cache_dir.glob("*.pkl"):
            try:
                cache_file.unlink()
            except Exception:
                pass


# Instância global do cache
cache_manager = CacheManager()


def cached(ttl: int = 3600, key_prefix: str = ""):
    """
    Decorador para cache automático de funções.
    
    Args:
        ttl: Time to live em segundos
        key_prefix: Prefixo para a chave do cache
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Gera chave do cache
            func_name = f"{key_prefix}{func.__name__}" if key_prefix else func.__name__
            cache_key = f"{func_name}_{cache_manager._generate_key(*args, **kwargs)}"
            
            # Tenta recuperar do cache
            cached_result = cache_manager.get(cache_key, ttl)
            if cached_result is not None:
                return cached_result
            
            # Executa função e armazena resultado
            result = func(*args, **kwargs)
            cache_manager.set(cache_key, result)
            
            return result
        
        return wrapper
    return decorator


def cached_dataframe(ttl: int = 1800):
    """
    Decorador específico para cache de DataFrames.
    
    Args:
        ttl: Time to live em segundos (padrão: 30 minutos)
    """
    return cached(ttl=ttl, key_prefix="df_")


def cached_query(ttl: int = 900):
    """
    Decorador específico para cache de consultas.
    
    Args:
        ttl: Time to live em segundos (padrão: 15 minutos)
    """
    return cached(ttl=ttl, key_prefix="query_")


# Funções de conveniência para pandas
@cached_dataframe(ttl=3600)
def load_csv_cached(file_path: Union[str, Path], **kwargs) -> pd.DataFrame:
    """
    Carrega CSV com cache automático.
    
    Args:
        file_path: Caminho do arquivo CSV
        **kwargs: Argumentos para pd.read_csv
        
    Returns:
        DataFrame carregado
    """
    return pd.read_csv(file_path, **kwargs)


@cached_query(ttl=1800)
def execute_groupby_cached(df: pd.DataFrame, group_cols: list, 
                          agg_dict: dict) -> pd.DataFrame:
    """
    Executa groupby com cache automático.
    
    Args:
        df: DataFrame
        group_cols: Colunas para agrupamento
        agg_dict: Dicionário de agregações
        
    Returns:
        DataFrame agrupado
    """
    return df.groupby(group_cols).agg(agg_dict)


def clear_all_cache():
    """Limpa todo o cache do sistema."""
    cache_manager.clear()


def get_cache_stats() -> Dict[str, Any]:
    """Retorna estatísticas do cache."""
    cache_files = list(cache_manager.cache_dir.glob("*.pkl"))
    total_size = sum(f.stat().st_size for f in cache_files)
    
    return {
        "memory_items": len(cache_manager.memory_cache),
        "disk_files": len(cache_files),
        "total_disk_size_mb": total_size / (1024 * 1024),
        "cache_directory": str(cache_manager.cache_dir)
    }