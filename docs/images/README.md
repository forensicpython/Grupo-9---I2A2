# 📸 Imagens da Documentação

Este diretório contém as capturas de tela e imagens usadas na documentação do Hánotas.

## 📁 **Estrutura de Arquivos**

```
docs/images/
├── dashboard.png           # Dashboard principal
├── api-config.png         # Configuração de API
├── analysis-interface.png # Interface de análise
├── terminal-logs.png      # Logs do terminal
└── README.md             # Este arquivo
```

## 📝 **Como Adicionar Imagens**

### **1. Capturar Screenshots**
- Use **cmd/ctrl + shift + 4** (macOS) ou **Windows + Shift + S** (Windows)
- Capture em **resolução alta** (mínimo 1920x1080)
- Mantenha **qualidade boa** mas arquivo **otimizado**

### **2. Nomear Arquivos**
- Use nomes **descritivos** em inglês
- Formato: `funcionalidade-contexto.png`
- Exemplos:
  - `dashboard-overview.png`
  - `upload-process.png`
  - `analysis-results.png`

### **3. Otimizar Imagens**
```bash
# Usando ImageMagick (instale primeiro)
magick input.png -quality 85 -resize 1920x1080> output.png

# Usando TinyPNG online
# https://tinypng.com/
```

### **4. Adicionar ao README Principal**
```markdown
![Description](docs/images/filename.png)
```

## 📋 **Screenshots Necessários**

### ✅ **Capturar Estas Telas:**

1. **Dashboard Principal** (`dashboard.png`)
   - Tela inicial com todos os menus
   - Central de ajuda visível
   - Interface limpa e organizada

2. **Configuração de API** (`api-config.png`)
   - Modal/página de configuração
   - Campo para chave Groq
   - Botão de teste de conexão

3. **Interface de Análise** (`analysis-interface.png`)
   - Upload de arquivo
   - Campo de pergunta
   - Área de resposta
   - Chat completo

4. **Terminal Verbose** (`terminal-logs.png`)
   - Logs em tempo real
   - Processamento dos agentes
   - WebSocket funcionando

5. **Resultados de Análise** (`analysis-results.png`)
   - Resposta formatada
   - Insights gerados
   - Sugestões automáticas

6. **Mobile/Responsivo** (`mobile-interface.png`)
   - Interface em dispositivo móvel
   - Menu hamburger
   - Layout responsivo

## 🎨 **Diretrizes de Design**

### **Qualidade**
- **Resolução**: Mínimo 1920x1080
- **Formato**: PNG (transparência) ou JPG (fotos)
- **Tamanho**: Máximo 2MB por imagem

### **Conteúdo**
- **Dados reais** mas **não sensíveis**
- **Interface limpa** sem elementos de debug
- **Zoom apropriado** para legibilidade
- **Foco no contexto** relevante

### **Consistência**
- **Mesmo tema** do browser/OS quando possível
- **Tamanho de janela** consistente
- **Nível de zoom** similar

## 🔧 **Ferramentas Recomendadas**

### **Captura**
- **macOS**: Cmd+Shift+4 (nativo)
- **Windows**: Windows+Shift+S (nativo)
- **Linux**: Flameshot, GNOME Screenshot
- **Extensão**: Awesome Screenshot (browser)

### **Edição**
- **Básica**: Preview (macOS), Paint (Windows)
- **Avançada**: GIMP (gratuito), Photoshop
- **Online**: Photopea, Canva

### **Otimização**
- **TinyPNG**: https://tinypng.com/
- **ImageOptim**: https://imageoptim.com/
- **Squoosh**: https://squoosh.app/

## 📱 **Capturas Mobile**

### **Como Simular**
```javascript
// No DevTools do Chrome/Firefox
// 1. F12 para abrir DevTools
// 2. Clique no ícone de dispositivo móvel
// 3. Selecione iPhone/Android
// 4. Capture normalmente
```

### **Resoluções Comuns**
- **iPhone 14**: 390x844
- **Galaxy S21**: 384x854
- **iPad**: 768x1024

## 🚀 **Automação (Futuro)**

### **Playwright Screenshots**
```javascript
// Futuro: Automatizar capturas
const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.goto('http://localhost:5173');
  await page.screenshot({ path: 'dashboard.png' });
  await browser.close();
})();
```

---

## 📞 **Precisa de Ajuda?**

- 📧 **Contato**: [Equipe Grupo 9](../README.md#-equipe---grupo-9)
- 🐛 **Issues**: [GitHub Issues](https://github.com/forensicpython/Grupo-9---I2A2/issues)
- 💬 **Discussões**: [GitHub Discussions](https://github.com/forensicpython/Grupo-9---I2A2/discussions)

---

<div align="center">

**🎯 Capturas de qualidade fazem toda a diferença na documentação!**

*Desenvolvido com ❤️ pelo Grupo 9*

</div>