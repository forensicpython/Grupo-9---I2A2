from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional
import pandas as pd

class NotaFiscalCabecalho(BaseModel):
    """Modelo para validação dos cabeçalhos de notas fiscais baseado nos campos reais do CSV"""
    NUMERO: str = Field(..., description="Número da nota fiscal", alias="NÚMERO")
    DATA_EMISSAO: datetime = Field(..., description="Data de emissão da nota fiscal", alias="DATA EMISSÃO")
    CPF_CNPJ_Emitente: str = Field(..., description="CNPJ do emitente", alias="CPF/CNPJ Emitente")
    RAZAO_SOCIAL_EMITENTE: str = Field(..., description="Nome do emitente", alias="RAZÃO SOCIAL EMITENTE")
    VALOR_NOTA_FISCAL: float = Field(..., description="Valor total da nota fiscal", alias="VALOR NOTA FISCAL")
    UF_EMITENTE: Optional[str] = Field(None, description="Estado do emitente", alias="UF EMITENTE")
    MUNICIPIO_EMITENTE: Optional[str] = Field(None, description="Cidade do emitente", alias="MUNICÍPIO EMITENTE")
    CHAVE_DE_ACESSO: Optional[str] = Field(None, description="Chave de acesso da NF-e", alias="CHAVE DE ACESSO")
    CNPJ_DESTINATARIO: Optional[str] = Field(None, description="CNPJ do destinatário", alias="CNPJ DESTINATÁRIO")
    NOME_DESTINATARIO: Optional[str] = Field(None, description="Nome do destinatário", alias="NOME DESTINATÁRIO")
    
    # Configuração para aceitar conversões automáticas
    class Config:
        str_strip_whitespace = True
        validate_assignment = True
        allow_population_by_field_name = True
    
    @validator('NUMERO', pre=True)
    def convert_numero_nf(cls, v):
        """Converte numero_nf para string"""
        return str(v) if v is not None else None
    
    @validator('DATA_EMISSAO', pre=True)
    def parse_data_emissao(cls, v):
        if isinstance(v, str):
            try:
                return datetime.strptime(v, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                try:
                    return datetime.strptime(v, '%Y-%m-%d')
                except ValueError:
                    raise ValueError(f"Formato de data inválido: {v}")
        return v
    
    @validator('CPF_CNPJ_Emitente', pre=True)
    def validate_cnpj(cls, v):
        if v is None:
            return None
        v_str = str(v)
        cnpj_limpo = ''.join(filter(str.isdigit, v_str))
        # Adiciona zeros à esquerda se necessário
        cnpj_limpo = cnpj_limpo.zfill(14)
        if len(cnpj_limpo) != 14:
            raise ValueError(f"CNPJ deve ter 14 dígitos: {v}")
        return cnpj_limpo
    
    @validator('VALOR_NOTA_FISCAL')
    def validate_valor_positivo(cls, v):
        if v < 0:
            raise ValueError("Valor total deve ser positivo")
        return v

class NotaFiscalItem(BaseModel):
    """Modelo para validação dos itens de notas fiscais baseado nos campos reais do CSV"""
    NUMERO: str = Field(..., description="Número da nota fiscal", alias="NÚMERO")
    NUMERO_PRODUTO: str = Field(..., description="Código do produto", alias="NÚMERO PRODUTO")
    DESCRICAO_DO_PRODUTO_SERVICO: str = Field(..., description="Descrição do produto", alias="DESCRIÇÃO DO PRODUTO/SERVIÇO")
    QUANTIDADE: float = Field(..., description="Quantidade do produto", alias="QUANTIDADE")
    VALOR_UNITARIO: float = Field(..., description="Valor unitário do produto", alias="VALOR UNITÁRIO")
    VALOR_TOTAL: float = Field(..., description="Valor total do item", alias="VALOR TOTAL")
    NCM_SH_TIPO_DE_PRODUTO: Optional[str] = Field(None, description="Categoria do produto", alias="NCM/SH (TIPO DE PRODUTO)")
    CHAVE_DE_ACESSO: Optional[str] = Field(None, description="Chave de acesso da NF-e", alias="CHAVE DE ACESSO")
    CPF_CNPJ_Emitente: Optional[str] = Field(None, description="CNPJ do emitente", alias="CPF/CNPJ Emitente")
    RAZAO_SOCIAL_EMITENTE: Optional[str] = Field(None, description="Nome do emitente", alias="RAZÃO SOCIAL EMITENTE")
    
    # Configuração para aceitar conversões automáticas
    class Config:
        str_strip_whitespace = True
        validate_assignment = True
        allow_population_by_field_name = True
    
    @validator('NUMERO', 'NUMERO_PRODUTO', pre=True)
    def convert_to_string(cls, v):
        """Converte campos numéricos para string quando necessário"""
        return str(v) if v is not None else None
    
    @validator('QUANTIDADE', 'VALOR_UNITARIO', 'VALOR_TOTAL', pre=True)
    def validate_valores_positivos(cls, v):
        if v is None:
            return None
        v_float = float(v) if not isinstance(v, float) else v
        if v_float < 0:
            raise ValueError("Valores devem ser positivos")
        return v_float
    
    @validator('VALOR_TOTAL')
    def validate_calculo_total(cls, v, values):
        if 'QUANTIDADE' in values and 'VALOR_UNITARIO' in values:
            total_calculado = values['QUANTIDADE'] * values['VALOR_UNITARIO']
            if abs(v - total_calculado) > 0.01:  # Tolerância para arredondamento
                raise ValueError(f"Valor total inconsistente: {v} != {total_calculado}")
        return v

class ProcessamentoResult(BaseModel):
    sucesso: bool = Field(..., description="Indica se o processamento foi bem-sucedido")
    mensagem: str = Field(..., description="Mensagem de resultado")
    total_cabecalhos: int = Field(0, description="Total de cabeçalhos processados")
    total_itens: int = Field(0, description="Total de itens processados")
    erros: list = Field(default_factory=list, description="Lista de erros encontrados")

def validar_dataframe_cabecalho(df: pd.DataFrame) -> ProcessamentoResult:
    """Valida um DataFrame de cabeçalhos de notas fiscais"""
    erros = []
    registros_validos = 0
    
    for index, row in df.iterrows():
        try:
            NotaFiscalCabecalho(**row.to_dict())
            registros_validos += 1
        except Exception as e:
            erros.append(f"Linha {index + 1}: {str(e)}")
    
    return ProcessamentoResult(
        sucesso=len(erros) == 0,
        mensagem=f"Processados {registros_validos} cabeçalhos válidos de {len(df)} total",
        total_cabecalhos=registros_validos,
        erros=erros
    )

def validar_dataframe_itens(df: pd.DataFrame) -> ProcessamentoResult:
    """Valida um DataFrame de itens de notas fiscais"""
    erros = []
    registros_validos = 0
    
    for index, row in df.iterrows():
        try:
            NotaFiscalItem(**row.to_dict())
            registros_validos += 1
        except Exception as e:
            erros.append(f"Linha {index + 1}: {str(e)}")
    
    return ProcessamentoResult(
        sucesso=len(erros) == 0,
        mensagem=f"Processados {registros_validos} itens válidos de {len(df)} total",
        total_itens=registros_validos,
        erros=erros
    )

# Modelos de compatibilidade para manter funcionamento das ferramentas existentes
class NotaFiscalCabecalhoLegacy(BaseModel):
    """Modelo legacy para compatibilidade com ferramentas existentes"""
    numero_nf: str = Field(..., description="Número da nota fiscal")
    data_emissao: datetime = Field(..., description="Data de emissão da nota fiscal")
    cnpj_emitente: str = Field(..., description="CNPJ do emitente")
    nome_emitente: str = Field(..., description="Nome do emitente")
    valor_total: float = Field(..., description="Valor total da nota fiscal")
    estado: Optional[str] = Field(None, description="Estado do emitente")
    cidade: Optional[str] = Field(None, description="Cidade do emitente")
    
    class Config:
        str_strip_whitespace = True
        validate_assignment = True

class NotaFiscalItemLegacy(BaseModel):
    """Modelo legacy para compatibilidade com ferramentas existentes"""
    numero_nf: str = Field(..., description="Número da nota fiscal")
    codigo_produto: str = Field(..., description="Código do produto")
    descricao_produto: str = Field(..., description="Descrição do produto")
    quantidade: float = Field(..., description="Quantidade do produto")
    valor_unitario: float = Field(..., description="Valor unitário do produto")
    valor_total_item: float = Field(..., description="Valor total do item")
    categoria: Optional[str] = Field(None, description="Categoria do produto")
    
    class Config:
        str_strip_whitespace = True
        validate_assignment = True