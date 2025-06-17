# 🤖 Instaprice - Sistema Inteligente de Análise de Notas Fiscais

Sistema multi-agente baseado em CrewAI para análise inteligente de notas fiscais brasileiras. Utiliza processamento de linguagem natural para responder perguntas sobre dados fiscais de forma humanizada e inteligente.

## ✨ Características

- **Sistema Multi-Agente**: 6 agentes especializados trabalhando em sequência
- **Processamento NLP**: Interpreta perguntas em linguagem natural
- **Validação Rigorosa**: Usa Pydantic para garantir integridade dos dados
- **Análise Inteligente**: Operações Pandas otimizadas
- **Respostas Humanizadas**: Comunicação amigável com emojis e formatação
- **Sugestões Inteligentes**: Gera automaticamente novas perguntas relevantes

## 🚀 Instalação Rápida

### 1. Configuração Automática
```bash
python setup.py
```

### 2. Configuração Manual

#### Instalar dependências:
```bash
pip install -r requirements.txt
```

#### Configurar variáveis de ambiente:
```bash
cp .env.example .env
# Edite o arquivo .env e configure sua GROQ_API_KEY
```

#### Validar instalação:
```bash
python test_instaprice.py
```

## 🎯 Como Usar

### Execução Básica
```bash
python main_1.py              # Versão original
python main_melhorado.py      # Versão com logging melhorado
```

### Execução com Pergunta Customizada
```bash
PERGUNTA_USUARIO="Qual o valor médio das notas fiscais por fornecedor?" python main_melhorado.py
```

## 🏗️ Arquitetura do Sistema

### Fluxo de Processamento
```
ZIP → Extração → Validação → Interpretação → Análise → Humanização → Sugestões
```

### Agentes Especializados

1. **🔍 Zip Desbravador**
   - Extrai arquivos compactados
   - Suporta ZIP, 7Z, RAR
   - Organiza dados em `/dados/notasfiscais/`

2. **🛡️ Guardião Pydantic**
   - Valida estrutura dos dados
   - Garante consistência usando Pydantic
   - Gera relatórios de qualidade

3. **🧠 Linguista Lúcido**
   - Interpreta perguntas em linguagem natural
   - Usa busca semântica (RAG)
   - Mapeia consultas para operações de dados

4. **⚡ Executor de Consultas**
   - Executa operações Pandas
   - Realiza agregações e análises
   - Processa dados validados

5. **🎭 RP Lúdico**
   - Humaniza respostas técnicas
   - Adiciona emojis e formatação
   - Mantém tom profissional e amigável

6. **💡 Sugestor Visionário**
   - Gera 3 sugestões inteligentes
   - Explora diferentes dimensões dos dados
   - Estimula descobertas adicionais

## 📊 Estrutura de Dados

### Dados de Entrada
- **Arquivo ZIP**: Contendo CSVs de notas fiscais
- **Formato Esperado**:
  - `*cabecalho*.csv`: Dados dos cabeçalhos
  - `*itens*.csv`: Dados dos itens

### Modelos de Validação
- **NotaFiscalCabecalho**: Valida cabeçalhos das NFs
- **NotaFiscalItem**: Valida itens das NFs
- **ProcessamentoResult**: Resultado das validações

## 🛠️ Ferramentas Disponíveis

| Ferramenta | Função | Suporte |
|------------|---------|---------|
| `zip_extractor_tool` | Extração de arquivos | ZIP, 7Z, RAR, ARJ |
| `csv_validator_tool` | Validação Pydantic | CSV com validação rigorosa |
| `pandas_query_tool` | Análise de dados | Operações Pandas otimizadas |
| `rag_tool` | Busca semântica | Interpretação de consultas |

## 🔧 Configuração Avançada

### Variáveis de Ambiente
```bash
# Obrigatório
GROQ_API_KEY=sua_chave_groq_aqui

# Opcional
MODEL=llama-3.1-8b-instant
LOG_LEVEL=INFO
PERGUNTA_USUARIO="Sua pergunta personalizada"
```

### Modelos LLM Suportados
- llama-3.1-8b-instant (padrão)
- llama-3.1-70b-versatile
- mixtral-8x7b-32768

## 📝 Exemplos de Uso

### Perguntas Típicas
```python
"Quais são os principais fornecedores e seus valores totais?"
"Qual o valor médio das notas fiscais por mês?"
"Quais produtos têm maior volume de vendas?"
"Como está distribuída a receita por estado?"
"Quais fornecedores têm maior ticket médio?"
```

### Análises Disponíveis
- ✅ Análise de fornecedores
- ✅ Distribuição temporal
- ✅ Análise de produtos
- ✅ Distribuição geográfica
- ✅ Análise de valores e volumes
- ✅ Comparações e tendências

## 🔍 Solução de Problemas

### Problemas Comuns

**❌ Erro: GROQ_API_KEY não configurada**
```bash
# Configure sua chave no arquivo .env
echo "GROQ_API_KEY=sua_chave_aqui" >> .env
```

**❌ Erro: Arquivo ZIP não encontrado**
```bash
# Verifique se o arquivo existe
ls -la *.zip
```

**❌ Erro: Dependências não instaladas**
```bash
# Reinstale as dependências
pip install -r requirements.txt
```

### Logs e Diagnóstico
```bash
# Execute diagnóstico completo
python test_instaprice.py

# Verifique logs de execução
ls -la logs/

# Analise logs específicos
tail -f logs/instaprice_*.log
```

## 🚀 Melhorias Implementadas

### ✅ Funcionalidades Adicionadas
- Sistema de logging completo
- Validação de ambiente automatizada
- Script de setup automático
- Tratamento robusto de erros
- Arquivo de requirements
- Documentação completa

### ✅ Melhorias de Código
- Modularização do código
- Padrões de nomenclatura consistentes
- Tratamento de exceções
- Validação de dados entrada
- Sistema de logging estruturado

## 🤝 Contribuindo

1. Faça um fork do projeto
2. Crie uma branch para sua feature
3. Implemente suas melhorias
4. Execute os testes: `python test_instaprice.py`
5. Envie um pull request

## 📄 Licença

Este projeto está sob licença MIT. Veja o arquivo LICENSE para mais detalhes.

## 🆘 Suporte

Para suporte e dúvidas:
- Execute `python test_instaprice.py` para diagnóstico
- Verifique logs em `logs/`
- Consulte a documentação técnica do projeto

---

**Desenvolvido com ❤️ usando CrewAI e Python**