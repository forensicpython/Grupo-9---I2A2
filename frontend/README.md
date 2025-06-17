# ⚛️ Instaprice Frontend

Interface moderna e responsiva para o sistema de análise fiscal inteligente Instaprice.

## 🚀 Tecnologias

- **React 19** - Interface de usuário
- **Vite** - Build tool rápido e moderno
- **Tailwind CSS** - Estilização utilitária
- **Axios** - Cliente HTTP
- **jsPDF** - Geração de PDFs
- **WebSocket** - Comunicação em tempo real

## 📋 Funcionalidades

- 🔐 **Autenticação** - Sistema de login integrado
- 📤 **Upload de Arquivos** - Drag & drop para ZIP/CSV
- 💬 **Chat Inteligente** - Interface de perguntas em linguagem natural
- 📊 **Dashboard** - Visualização de análises
- 📄 **Exportação PDF** - Download de relatórios completos
- 🔗 **Terminal Integrado** - Logs em tempo real via WebSocket

## 🏃‍♂️ Desenvolvimento

### Instalação
```bash
npm install
```

### Executar em desenvolvimento
```bash
npm run dev
```

### Build para produção
```bash
npm run build
```

### Preview da build
```bash
npm run preview
```

## 🎨 Estrutura do Projeto

```
src/
├── components/          # Componentes reutilizáveis
│   ├── ApiTest.jsx     # Teste de conexão com API
│   ├── FileUpload.jsx  # Component de upload
│   └── TerminalView.jsx # Terminal WebSocket
├── pages/              # Páginas principais
│   ├── LoginPage.jsx   # Página de login
│   ├── Dashboard.jsx   # Dashboard principal
│   └── AnalysisPage.jsx # Interface de análise
├── services/           # Serviços de API
│   └── api.js         # Cliente HTTP
├── config/            # Configurações
│   └── timeouts.js    # Timeouts personalizados
├── utils/             # Utilitários
│   └── websocket.js   # WebSocket client
└── assets/            # Recursos estáticos
    └── instaprice.png # Logo do projeto
```

## ⚙️ Configuração

### Variáveis de Ambiente

Crie um arquivo `.env` na raiz do frontend:

```bash
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000
```

### Timeouts Personalizados

Os timeouts estão configurados em `src/config/timeouts.js`:

```javascript
export const TIMEOUTS = {
  API: {
    PROCESSING: 900000,  // 15min para processamento CrewAI
    UPLOAD: 120000,      // 2min para upload
  },
  WEBSOCKET: {
    HEARTBEAT: 30000,    // 30s heartbeat
    RECONNECT: 5000,     // 5s reconexão
  }
}
```

## 🔧 Scripts Disponíveis

- `npm run dev` - Servidor de desenvolvimento
- `npm run build` - Build para produção
- `npm run preview` - Preview da build
- `npm run lint` - Verificação de código
- `npm run lint:fix` - Correção automática

## 🌟 Funcionalidades Avançadas

### Upload Inteligente
- Suporte a múltiplos formatos (ZIP, CSV, Excel)
- Validação de tamanho e tipo
- Progress indicator
- Drag & drop interface

### WebSocket Real-time
- Logs do backend em tempo real
- Heartbeat automático
- Reconexão inteligente
- Status de conexão visual

### Exportação PDF
- Conversas completas
- Logs formatados
- Download automático
- Layout profissional

## 🔍 Solução de Problemas

### Problemas Comuns

**❌ Frontend não conecta ao backend**
```bash
# Verifique se o backend está rodando
curl http://localhost:8000/health

# Verifique as variáveis de ambiente
cat .env
```

**❌ WebSocket não conecta**
```bash
# Verifique se o WebSocket está habilitado no backend
# Teste a URL: ws://localhost:8000/ws
```

**❌ Build falha**
```bash
# Limpe node_modules e reinstale
rm -rf node_modules package-lock.json
npm install
```

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch para sua feature
3. Implemente suas melhorias
4. Execute `npm run lint` para verificar o código
5. Envie um pull request

---

**Desenvolvido com ❤️ pelo Grupo 9 - Desafio I2A2 2025**