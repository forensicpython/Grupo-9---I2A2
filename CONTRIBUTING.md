# 🤝 Guia de Contribuição - Instaprice

Obrigado por considerar contribuir para o **Instaprice**! 🎉

Este documento fornece diretrizes para contribuir com o projeto de forma eficiente e organizada.

## 🌟 Como Contribuir

### 1. **🍴 Fork do Repositório**
```bash
# Fork o projeto no GitHub
# Clone seu fork
git clone https://github.com/SEU_USUARIO/instaprice.git
cd instaprice

# Adicione o repositório original como upstream
git remote add upstream https://github.com/ORIGINAL_REPO/instaprice.git
```

### 2. **🌿 Crie uma Branch**
```bash
# Crie uma branch para sua funcionalidade
git checkout -b feature/nome-da-funcionalidade

# Ou para correção de bug
git checkout -b fix/nome-do-bug

# Ou para documentação
git checkout -b docs/melhoria-documentacao
```

### 3. **💻 Desenvolva**
- Siga os [padrões de código](#-padrões-de-código)
- Adicione testes quando necessário
- Atualize a documentação relevante

### 4. **✅ Teste**
```bash
# Backend
cd backend
pytest test_*.py -v

# Frontend  
cd frontend
npm test

# Teste manual completo
python test_instaprice.py
```

### 5. **📤 Envie**
```bash
# Commit suas mudanças
git add .
git commit -m "feat: adiciona nova funcionalidade X"

# Push para sua branch
git push origin feature/nome-da-funcionalidade

# Abra um Pull Request no GitHub
```

## 📝 **Padrões de Código**

### **🐍 Python (Backend)**

#### **Estilo de Código**
```python
# Use type hints
def process_file(file_path: str, options: Dict[str, Any]) -> ProcessResult:
    """Processa arquivo com opções especificadas."""
    pass

# Nomes descritivos
def validate_nota_fiscal_data(csv_data: pd.DataFrame) -> ValidationResult:
    pass

# Docstrings para funções públicas
def extract_zip_file(zip_path: str, destination: str) -> bool:
    """
    Extrai arquivo ZIP para diretório de destino.
    
    Args:
        zip_path: Caminho para o arquivo ZIP
        destination: Diretório de destino
        
    Returns:
        True se extraiu com sucesso, False caso contrário
    """
```

#### **Estrutura de Arquivos**
```
backend/
├── agents/           # Definições dos agentes
├── tools/           # Ferramentas especializadas  
├── models/          # Modelos Pydantic
├── utils/           # Utilitários
├── config/          # Configurações
└── tests/           # Testes
```

### **⚛️ React (Frontend)**

#### **Componentes**
```jsx
// Use functional components com hooks
const AnalysisPage = ({ user }) => {
  const [data, setData] = useState(null)
  
  // Nomes descritivos para funções
  const handleFileUpload = async (file) => {
    // ...
  }
  
  return (
    <div className="container">
      {/* JSX bem estruturado */}
    </div>
  )
}

export default AnalysisPage
```

#### **Estilização**
```jsx
// Use Tailwind CSS consistentemente
<button className="px-4 py-2 bg-instaprice-primary text-white rounded-lg 
                 hover:bg-instaprice-secondary transition-colors">
  Analisar
</button>

// Classes customizadas em src/index.css quando necessário
```

### **📏 Formatação**

#### **Python**
```bash
# Use black para formatação
black .

# Use isort para imports
isort .

# Use flake8 para linting
flake8 .
```

#### **JavaScript/React**
```bash
# Use Prettier para formatação
npm run format

# Use ESLint para linting  
npm run lint
```

## 🧪 **Diretrizes de Testes**

### **📊 Backend Tests**
```python
# test_agents.py
def test_zip_extractor_valid_file():
    """Testa extração de arquivo ZIP válido."""
    result = zip_extractor.extract("test.zip", "output/")
    assert result.success is True
    assert len(result.files) > 0

def test_pydantic_validator_invalid_data():
    """Testa validação com dados inválidos."""
    with pytest.raises(ValidationError):
        NotaFiscalCabecalho(cnpj="invalid")
```

### **🎭 Frontend Tests**
```jsx
// AnalysisPage.test.jsx  
import { render, screen, fireEvent } from '@testing-library/react'
import AnalysisPage from './AnalysisPage'

test('renders analysis page', () => {
  render(<AnalysisPage />)
  expect(screen.getByText('Análise Inteligente')).toBeInTheDocument()
})

test('handles file upload', async () => {
  render(<AnalysisPage />)
  const uploadButton = screen.getByText('Upload')
  fireEvent.click(uploadButton)
  // Adicione asserções
})
```

### **🔄 E2E Tests**
```javascript
// tests/e2e/analysis.spec.js
test('complete analysis workflow', async ({ page }) => {
  await page.goto('http://localhost:5173')
  await page.click('[data-testid="upload-button"]')
  await page.setInputFiles('[data-testid="file-input"]', 'test.zip')
  await page.click('[data-testid="analyze-button"]')
  
  await expect(page.locator('[data-testid="results"]')).toBeVisible()
})
```

## 📋 **Tipos de Contribuição**

### 🆕 **Novas Funcionalidades**
- Novos agentes especializados
- Ferramentas de análise
- Melhorias de UI/UX
- Integrações com APIs

### 🐛 **Correção de Bugs**
- Problemas de conectividade
- Erros de validação
- Issues de performance
- Bugs de interface

### 📚 **Documentação**
- Melhorias no README
- Documentação de API
- Tutoriais e exemplos
- Tradução de conteúdo

### 🔧 **Melhorias Técnicas**
- Otimizações de performance
- Refatoração de código
- Melhorias de segurança
- Configuração de CI/CD

## 💬 **Padrões de Commit**

Use **Conventional Commits**:

```bash
# Funcionalidades
git commit -m "feat: adiciona novo agente de análise temporal"
git commit -m "feat(ui): implementa modo escuro"

# Correções
git commit -m "fix: corrige timeout em uploads grandes" 
git commit -m "fix(api): resolve erro de validação de CNPJ"

# Documentação
git commit -m "docs: atualiza guia de instalação"
git commit -m "docs(api): adiciona exemplos de uso"

# Refatoração
git commit -m "refactor: reorganiza estrutura de agentes"
git commit -m "refactor(utils): melhora função de validação"

# Testes
git commit -m "test: adiciona testes para componente Upload"
git commit -m "test(e2e): implementa teste de fluxo completo"

# Configuração
git commit -m "chore: atualiza dependências"
git commit -m "chore(ci): configura GitHub Actions"
```

## 🔍 **Processo de Review**

### **📋 Checklist do Pull Request**
- [ ] Código segue os padrões estabelecidos
- [ ] Testes passam (`npm test` e `pytest`)
- [ ] Documentação atualizada quando necessário
- [ ] Commit messages seguem padrão
- [ ] Funcionalidade testada manualmente
- [ ] Sem comentários de debug ou código comentado
- [ ] Variáveis sensíveis não expostas

### **📝 Template de PR**
```markdown
## 📄 Descrição
Breve descrição das mudanças implementadas.

## 🔄 Tipo de Mudança
- [ ] Bug fix
- [ ] Nova funcionalidade  
- [ ] Breaking change
- [ ] Documentação

## 🧪 Como Testar
1. Clone a branch
2. Execute `npm install`
3. Execute `npm test`
4. Teste manualmente: [descrever passos]

## 📷 Screenshots (se aplicável)
[Adicione screenshots para mudanças de UI]

## ✅ Checklist
- [ ] Testes passando
- [ ] Documentação atualizada
- [ ] Código revisado
```

## 🤝 **Diretrizes da Comunidade**

### **💬 Comunicação**
- Seja respeitoso e construtivo
- Use linguagem clara e objetiva
- Forneça contexto suficiente
- Agradeça feedback recebido

### **🔍 Issues**
```markdown
# 🐛 Bug Report
**Descrição:** [Descreva o problema]
**Passos para reproduzir:** [Lista numerada]
**Comportamento esperado:** [O que deveria acontecer]
**Ambiente:** [OS, versão do Python/Node, etc.]

# 💡 Feature Request  
**Descrição:** [Descreva a funcionalidade]
**Justificativa:** [Por que é importante]
**Proposta:** [Como implementar]
```

### **❓ Dúvidas**
- Verifique a documentação primeiro
- Procure em issues existentes
- Use títulos descritivos
- Forneça contexto completo

## 🏆 **Reconhecimento**

Contribuidores ativos serão:
- Mencionados no README.md
- Adicionados ao arquivo CONTRIBUTORS.md
- Reconhecidos nas release notes

## 📞 **Contato**

- **🐛 Issues**: Use GitHub Issues
- **💬 Discussões**: GitHub Discussions  
- **📧 Email**: Contate a [equipe do projeto](mailto:juliana.coelho@live.com)

---

## 🎯 **Primeiras Contribuições**

Novo no projeto? Comece com:

1. **🔰 Issues marcadas como "good first issue"**
2. **📝 Melhorias na documentação**
3. **🧪 Adição de testes**
4. **🐛 Correção de bugs pequenos**

Sinta-se à vontade para fazer perguntas! A comunidade está aqui para ajudar. 🤗

---

**Obrigado por contribuir com o Instaprice! 🚀**

*Desenvolvido com ❤️ pelo Grupo 9*