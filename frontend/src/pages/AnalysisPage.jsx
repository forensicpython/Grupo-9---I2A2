import { useState, useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { 
  ArrowLeft, 
  MessageSquare, 
  Send, 
  Lightbulb, 
  FileText, 
  Download,
  BarChart3,
  TrendingUp,
  AlertTriangle,
  Terminal
} from 'lucide-react'
import { filesAPI } from '../services/api'
import { wsManager } from '../utils/websocket'
import instaprice from '../assets/instaprice.png'
import jsPDF from 'jspdf'

const AnalysisPage = ({ user }) => {
  const [messages, setMessages] = useState([])
  const [inputMessage, setInputMessage] = useState('')
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [analysisData, setAnalysisData] = useState(null)
  const [agentLogs, setAgentLogs] = useState([])
  const [sessionId, setSessionId] = useState(null)
  const [isSessionReady, setIsSessionReady] = useState(false)
  const logsEndRef = useRef(null)
  const navigate = useNavigate()

  useEffect(() => {
    // Carrega dados da análise do localStorage
    const savedData = localStorage.getItem('analysisData')
    if (savedData) {
      const data = JSON.parse(savedData)
      setAnalysisData(data)
      console.log('AnalysisPage: Dados carregados:', data)
    } else {
      // Se não há dados, volta para o dashboard
      navigate('/dashboard')
    }

    // Conecta WebSocket para logs em tempo real
    wsManager.connect('ws://localhost:8000/ws')
    
    // Listener para logs dos agentes
    wsManager.on('agent_log', (data) => {
      console.log('AnalysisPage: Log recebido:', data.data)
      
      // Se é output real do terminal, adiciona exatamente como veio
      if (data.data.raw_terminal) {
        addAgentLog('Terminal', data.data.message, 'raw_terminal')
      } else {
        addAgentLog(
          data.data.agent || 'Sistema',
          data.data.message,
          data.data.log_type || data.data.level || 'info'
        )
      }
    })

    // Cleanup on unmount
    return () => {
      wsManager.disconnect()
    }
  }, [])

  // Auto-scroll para novos logs
  useEffect(() => {
    if (logsEndRef.current) {
      logsEndRef.current.scrollIntoView({ behavior: 'smooth' })
    }
  }, [agentLogs])

  const addAgentLog = (agent, message, type = 'info') => {
    const newLog = {
      timestamp: new Date().toLocaleTimeString(),
      agent: agent,
      message: message,
      type: type
    }
    setAgentLogs(prev => [...prev, newLog])
  }

  const suggestions = [
    "Quais são as principais inconsistências nos dados das notas fiscais?",
    "Mostre um resumo dos produtos mais vendidos",
    "Identifique possíveis fraudes ou anomalias nos valores"
  ]

  const handleSendMessage = async (message = inputMessage) => {
    if (!message.trim() || !analysisData) return

    const userMessage = {
      id: Date.now(),
      text: message,
      sender: 'user',
      timestamp: new Date().toLocaleTimeString()
    }

    setMessages(prev => [...prev, userMessage])
    setInputMessage('')
    setIsAnalyzing(true)
    
    // Limpa logs anteriores apenas na primeira execução
    if (!isSessionReady) {
      setAgentLogs([])
    }
    addAgentLog('Sistema', '🚀 Iniciando análise com CrewAI...', 'info')

    try {
      let response;
      
      if (!isSessionReady || !sessionId) {
        // Primeira execução - processa arquivo completo
        console.log('AnalysisPage: Primeira execução - processando arquivo:', {
          fileId: analysisData.file.serverFileId,
          pergunta: message,
          apiKey: '***',
          model: analysisData.model
        })

        response = await filesAPI.process(
          analysisData.file.serverFileId, 
          message,
          analysisData.apiKey,
          analysisData.model
        )
        
        // Salva session_id da resposta
        if (response.data.session_id) {
          setSessionId(response.data.session_id)
          setIsSessionReady(true)
          console.log('AnalysisPage: Sessão criada:', response.data.session_id)
        }
      } else {
        // Execuções subsequentes - usa sessão existente
        console.log('AnalysisPage: Consulta adicional na sessão:', {
          sessionId: sessionId,
          pergunta: message
        })

        response = await fetch(`http://localhost:8000/api/query/${sessionId}`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ question: message })
        })

        if (!response.ok) {
          throw new Error(`Erro na consulta: ${response.statusText}`)
        }

        response = { data: await response.json() }
      }
      
      const aiResponse = {
        id: Date.now() + 1,
        text: response.data.response || response.data.results?.resposta || 'Análise concluída com sucesso!',
        sender: 'ai',
        timestamp: new Date().toLocaleTimeString(),
        results: response.data.results
      }
      
      setMessages(prev => [...prev, aiResponse])
      addAgentLog('Sistema', '✅ Análise concluída com sucesso!', 'info')
      console.log('AnalysisPage: Resposta recebida:', response.data)
      
    } catch (error) {
      console.error('AnalysisPage: Erro na análise:', error)
      addAgentLog('Sistema', `❌ Erro durante processamento: ${error.message}`, 'error')
      
      const errorResponse = {
        id: Date.now() + 1,
        text: `❌ Erro na análise: ${error.message}. Verifique os logs para mais detalhes.`,
        sender: 'ai',
        timestamp: new Date().toLocaleTimeString(),
        error: true
      }
      setMessages(prev => [...prev, errorResponse])
    } finally {
      setIsAnalyzing(false)
    }
  }

  const generateAIResponse = (question) => {
    if (question.toLowerCase().includes('inconsistências')) {
      return `Analisando os dados das notas fiscais, identifiquei as seguintes inconsistências:

**Principais Problemas Encontrados:**
• 23 notas com valores de ICMS incorretos
• 15 registros com códigos de produto duplicados
• 8 notas fiscais com datas futuras
• 5 inconsistências entre valor total e soma dos itens

**Recomendações:**
1. Revisar o cálculo automático de impostos
2. Implementar validação de códigos únicos
3. Adicionar validação de datas
4. Verificar arredondamentos nos totais

Deseja que eu gere um relatório detalhado dessas inconsistências?`
    }
    
    if (question.toLowerCase().includes('vendidos') || question.toLowerCase().includes('resumo')) {
      return `**Resumo dos Produtos Mais Vendidos (Último Período)**

**Top 5 Produtos:**
1. **Notebook Dell Inspiron** - 156 unidades (R$ 187.400,00)
2. **Mouse Wireless Logitech** - 298 unidades (R$ 23.840,00)
3. **Teclado Mecânico RGB** - 187 unidades (R$ 28.050,00)
4. **Monitor 24" Full HD** - 98 unidades (R$ 78.400,00)
5. **Cabo USB-C** - 456 unidades (R$ 13.680,00)

**Insights:**
• Eletrônicos representam 78% das vendas
• Crescimento de 23% em periféricos
• Margem média de 35% nos produtos

Quer ver a análise temporal ou detalhamento por categoria?`
    }
    
    if (question.toLowerCase().includes('fraude') || question.toLowerCase().includes('anomalias')) {
      return `**Análise de Anomalias e Possíveis Fraudes**

⚠️ **Alertas Identificados:**

**Alto Risco:**
• 3 notas com valores muito acima da média (>500% do padrão)
• 2 fornecedores com padrão suspeito de faturamento
• 1 sequência de notas com numeração irregular

**Médio Risco:**
• 12 transações fora do horário comercial
• 8 notas com valores "redondos" suspeitos
• 5 duplicatas com pequenas variações

**Recomendações:**
✅ Implementar validação automática de valores extremos
✅ Monitorar fornecedores com comportamento atípico
✅ Revisar processos de emissão noturna

Deseja que eu aprofunde a investigação em algum caso específico?`
    }
    
    return `Entendi sua pergunta sobre "${question}". 

Com base nos dados analisados, posso fornecer insights detalhados sobre:
• Padrões de vendas e faturamento
• Análise de conformidade fiscal
• Identificação de anomalias
• Relatórios customizados

Como posso ajudar você especificamente com essa análise?`
  }

  const exportChatToPDF = () => {
    try {
      // Criar nova instância do jsPDF
      const doc = new jsPDF()
      
      // Configurações do PDF
      const pageWidth = doc.internal.pageSize.getWidth()
      const pageHeight = doc.internal.pageSize.getHeight()
      const margin = 20
      const maxWidth = pageWidth - (margin * 2)
      let currentY = margin
      
      // Função para adicionar nova página se necessário
      const checkNewPage = (lineHeight = 8) => {
        if (currentY + lineHeight > pageHeight - margin) {
          doc.addPage()
          currentY = margin
        }
      }
      
      // Função para quebrar texto em linhas
      const splitText = (text, maxWidth, fontSize = 10) => {
        doc.setFontSize(fontSize)
        return doc.splitTextToSize(text, maxWidth)
      }
      
      // Cabeçalho do PDF
      doc.setFontSize(16)
      doc.setFont('helvetica', 'bold')
      doc.text('Instaprice - Análise Inteligente de Notas Fiscais', margin, currentY)
      currentY += 10
      
      doc.setFontSize(12)
      doc.setFont('helvetica', 'normal')
      doc.text(`Relatório gerado em: ${new Date().toLocaleString('pt-BR')}`, margin, currentY)
      currentY += 8
      
      if (analysisData) {
        doc.text(`Arquivo: ${analysisData.file.name}`, margin, currentY)
        currentY += 6
        doc.text(`Modelo AI: ${analysisData.model}`, margin, currentY)
        currentY += 10
      }
      
      // Linha separadora
      doc.setLineWidth(0.5)
      doc.line(margin, currentY, pageWidth - margin, currentY)
      currentY += 15
      
      // Seção do Chat
      if (messages.length > 0) {
        doc.setFontSize(14)
        doc.setFont('helvetica', 'bold')
        doc.text('CONVERSAÇÃO DO CHAT', margin, currentY)
        currentY += 15
        
        messages.forEach((message, index) => {
          checkNewPage(20)
          
          // Rótulo do remetente
          doc.setFontSize(11)
          doc.setFont('helvetica', 'bold')
          const senderLabel = message.sender === 'user' ? 'USUÁRIO' : 'ASSISTENTE AI'
          const senderColor = message.sender === 'user' ? [0, 100, 200] : [0, 150, 0]
          doc.setTextColor(...senderColor)
          doc.text(`${senderLabel} [${message.timestamp}]:`, margin, currentY)
          currentY += 8
          
          // Conteúdo da mensagem
          doc.setTextColor(0, 0, 0)
          doc.setFont('helvetica', 'normal')
          doc.setFontSize(10)
          
          const messageLines = splitText(message.text, maxWidth, 10)
          messageLines.forEach(line => {
            checkNewPage()
            doc.text(line, margin, currentY)
            currentY += 5
          })
          
          currentY += 8 // Espaço entre mensagens
        })
        
        currentY += 10
      }
      
      // Seção dos Logs do Terminal
      if (agentLogs.length > 0) {
        checkNewPage(30)
        
        // Título da seção
        doc.setFontSize(14)
        doc.setFont('helvetica', 'bold')
        doc.setTextColor(0, 0, 0)
        doc.text('LOGS COMPLETOS DO TERMINAL VERBOSE', margin, currentY)
        currentY += 15
        
        doc.setFontSize(9)
        doc.setFont('helvetica', 'normal')
        doc.text('Saída completa dos agentes CrewAI durante o processamento:', margin, currentY)
        currentY += 15
        
        // Logs do terminal
        agentLogs.forEach((log, index) => {
          checkNewPage(12)
          
          if (log.type === 'raw_terminal') {
            // Output direto do terminal
            doc.setFont('courier', 'normal')
            doc.setFontSize(8)
            doc.setTextColor(0, 100, 0) // Verde para terminal
            
            // Limpa o texto de caracteres ANSI
            const cleanMessage = log.message.replace(/\[\d+m/g, '').replace(/\[0m/g, '')
            const terminalLines = splitText(cleanMessage, maxWidth, 8)
            
            terminalLines.forEach(line => {
              checkNewPage()
              doc.text(line, margin, currentY)
              currentY += 4
            })
          } else {
            // Logs do sistema
            doc.setFont('helvetica', 'normal')
            doc.setFontSize(9)
            doc.setTextColor(100, 100, 100) // Cinza para logs do sistema
            
            const logHeader = `[${log.timestamp}] ${log.agent}: `
            doc.text(logHeader, margin, currentY)
            currentY += 5
            
            doc.setTextColor(0, 0, 0)
            const systemLines = splitText(log.message, maxWidth - 20, 9)
            systemLines.forEach(line => {
              checkNewPage()
              doc.text(line, margin + 10, currentY)
              currentY += 4
            })
          }
          
          currentY += 3 // Pequeno espaço entre logs
        })
      }
      
      // Rodapé em todas as páginas
      const totalPages = doc.internal.getNumberOfPages()
      for (let i = 1; i <= totalPages; i++) {
        doc.setPage(i)
        doc.setFontSize(8)
        doc.setTextColor(128, 128, 128)
        doc.text(
          `Página ${i} de ${totalPages} - Instaprice AI Analysis`, 
          pageWidth / 2, 
          pageHeight - 10, 
          { align: 'center' }
        )
      }
      
      // Salvar o PDF
      const fileName = `instaprice-chat-${new Date().toISOString().slice(0, 10)}.pdf`
      doc.save(fileName)
      
      // Feedback visual
      addAgentLog('Sistema', `✅ Chat exportado como PDF: ${fileName}`, 'info')
      
    } catch (error) {
      console.error('Erro ao exportar PDF:', error)
      addAgentLog('Sistema', `❌ Erro ao exportar PDF: ${error.message}`, 'error')
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-instaprice-darker to-instaprice-dark">
      {/* Header */}
      <header className="bg-black/20 backdrop-blur-md border-b border-gray-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-4">
              <button
                onClick={() => navigate('/dashboard')}
                className="flex items-center space-x-2 text-gray-400 hover:text-white transition-colors"
              >
                <ArrowLeft className="w-5 h-5" />
                <span>Voltar</span>
              </button>
              <div className="h-6 w-px bg-gray-600"></div>
              <img src={instaprice} alt="Instaprice" className="h-16" />
              <div>
                <h1 className="text-xl font-bold text-white">Análise Inteligente</h1>
                <p className="text-sm text-gray-400">Faça perguntas em linguagem natural</p>
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              <button 
                onClick={exportChatToPDF}
                disabled={agentLogs.length === 0 && messages.length === 0}
                className="flex items-center space-x-2 px-4 py-2 bg-instaprice-primary/20 
                         border border-instaprice-primary/30 rounded-lg hover:bg-instaprice-primary/30 
                         transition-colors text-instaprice-primary disabled:opacity-50 
                         disabled:cursor-not-allowed"
                title="Exportar toda a conversação e logs do terminal para PDF"
              >
                <Download className="w-4 h-4" />
                <span>Exportar Chat</span>
              </button>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Chat Area */}
          <div className="lg:col-span-1">
            <div className="glass-effect rounded-xl overflow-hidden flex flex-col h-[600px]">
              {/* Chat Header */}
              <div className="bg-gray-900/50 px-6 py-4 border-b border-gray-700">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 bg-gradient-to-r from-instaprice-primary to-instaprice-secondary 
                                   rounded-full flex items-center justify-center">
                      <MessageSquare className="w-5 h-5 text-white" />
                    </div>
                    <div>
                      <h3 className="text-white font-medium">Assistente de Análise Fiscal</h3>
                      <p className="text-gray-400 text-sm">
                        {analysisData ? `${analysisData.model} • ${analysisData.file.name}` : 'Powered by Groq AI'}
                        {isSessionReady && <span className="text-green-400 ml-2">• Sessão ativa</span>}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
                    <span className="text-green-400 text-sm">Online</span>
                  </div>
                </div>
              </div>

              {/* Messages */}
              <div className="flex-1 overflow-y-auto p-6 space-y-4">
                {messages.length === 0 ? (
                  <div className="flex flex-col items-center justify-center h-full text-center">
                    <div className="w-16 h-16 bg-instaprice-primary/20 rounded-full flex items-center justify-center mb-4">
                      <MessageSquare className="w-8 h-8 text-instaprice-primary" />
                    </div>
                    <h3 className="text-white font-medium mb-2">Pronto para analisar seus dados</h3>
                    <p className="text-gray-400 max-w-md">
                      Faça qualquer pergunta sobre suas notas fiscais. Posso ajudar com análises, 
                      relatórios e identificação de anomalias.
                    </p>
                    {!isSessionReady && (
                      <p className="text-blue-400 text-sm mt-2 max-w-md">
                        💡 Após a primeira pergunta, você pode fazer perguntas adicionais sem recarregar os documentos!
                      </p>
                    )}
                  </div>
                ) : (
                  messages.map((message) => (
                    <div
                      key={message.id}
                      className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
                    >
                      <div
                        className={`max-w-[80%] p-4 rounded-2xl ${
                          message.sender === 'user'
                            ? 'bg-instaprice-primary text-white'
                            : 'bg-gray-800/50 text-gray-100'
                        }`}
                      >
                        <div className="whitespace-pre-wrap text-sm leading-relaxed">
                          {message.text}
                        </div>
                        {message.charts && (
                          <div className="mt-4 grid grid-cols-2 gap-4">
                            {message.charts.map((chart, index) => (
                              <div key={index} className="bg-gray-900/50 rounded-lg p-4">
                                <h4 className="text-xs font-medium text-gray-300 mb-2">{chart.title}</h4>
                                <div className="h-20 bg-gradient-to-r from-instaprice-primary/20 to-instaprice-secondary/20 
                                              rounded flex items-end justify-center">
                                  <BarChart3 className="w-8 h-8 text-instaprice-primary/50" />
                                </div>
                              </div>
                            ))}
                          </div>
                        )}
                        <div className="text-xs opacity-60 mt-2">
                          {message.timestamp}
                        </div>
                      </div>
                    </div>
                  ))
                )}
                
                {isAnalyzing && (
                  <div className="flex justify-start">
                    <div className="bg-gray-800/50 p-4 rounded-2xl">
                      <div className="flex items-center space-x-2">
                        <div className="flex space-x-1">
                          <div className="w-2 h-2 bg-instaprice-primary rounded-full animate-bounce"></div>
                          <div className="w-2 h-2 bg-instaprice-primary rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                          <div className="w-2 h-2 bg-instaprice-primary rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                        </div>
                        <span className="text-gray-400 text-sm">Analisando...</span>
                      </div>
                    </div>
                  </div>
                )}
              </div>

              {/* Input */}
              <div className="border-t border-gray-700 p-4">
                <div className="flex space-x-4">
                  <input
                    type="text"
                    value={inputMessage}
                    onChange={(e) => setInputMessage(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                    placeholder={isSessionReady ? "Faça outra pergunta sobre os mesmos dados..." : "Faça uma pergunta sobre suas notas fiscais..."}
                    className="flex-1 px-4 py-3 bg-gray-800/50 border border-gray-600 rounded-lg 
                             text-white placeholder-gray-400 focus:outline-none focus:ring-2 
                             focus:ring-instaprice-primary focus:border-transparent transition-all"
                  />
                  <button
                    onClick={() => handleSendMessage()}
                    disabled={!inputMessage.trim() || isAnalyzing}
                    className="px-6 py-3 bg-gradient-to-r from-instaprice-primary to-instaprice-secondary 
                             text-white rounded-lg font-medium hover:shadow-lg hover:shadow-instaprice-primary/25 
                             transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    <Send className="w-5 h-5" />
                  </button>
                </div>
              </div>
            </div>
          </div>

          {/* Agent Logs */}
          <div className="lg:col-span-1">
            <div className="glass-effect rounded-xl overflow-hidden flex flex-col h-[600px]">
              {/* Logs Header */}
              <div className="bg-gray-900/50 px-6 py-4 border-b border-gray-700">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 bg-gradient-to-r from-green-500 to-blue-500 
                                   rounded-full flex items-center justify-center">
                      <Terminal className="w-5 h-5 text-white" />
                    </div>
                    <div>
                      <h3 className="text-white font-medium">Terminal Verbose - Agentes CrewAI</h3>
                      <p className="text-gray-400 text-sm">Output completo do terminal de execução</p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
                    <span className="text-green-400 text-sm">Ativo</span>
                  </div>
                </div>
              </div>

              {/* Terminal Content */}
              <div className="flex-1 overflow-y-auto p-3 bg-black/80">
                <div className="space-y-1">
                  {agentLogs.length === 0 ? (
                    <div className="flex flex-col items-center justify-center h-full text-center py-12">
                      <Terminal className="w-12 h-12 text-gray-600 mb-3" />
                      <p className="text-gray-400">Terminal aguardando execução...</p>
                      <p className="text-gray-500 text-sm mt-1">
                        Todo o output verbose dos agentes CrewAI aparecerá aqui
                      </p>
                    </div>
                  ) : (
                    agentLogs.map((log, index) => (
                      <div
                        key={index}
                        className={`${
                          log.type === 'raw_terminal' 
                            ? 'text-green-300 font-mono text-xs leading-tight' 
                            : 'p-2 text-xs font-mono leading-relaxed bg-gray-800/40 border-l-4 border-gray-500 text-gray-200'
                        }`}
                      >
                        {log.type === 'raw_terminal' ? (
                          // Exibe output EXATO do terminal
                          <pre className="whitespace-pre-wrap text-green-300 font-mono text-xs leading-tight">
                            {log.message}
                          </pre>
                        ) : (
                          // Logs não-terminais (sistema, etc.)
                          <div className="flex items-start space-x-2">
                            <span className="text-gray-500 text-xs whitespace-nowrap flex-shrink-0 w-12">
                              {log.timestamp}
                            </span>
                            <div className="flex-1 min-w-0">
                              {log.agent && log.agent !== 'Sistema' && (
                                <div className="font-semibold mb-1 text-xs opacity-90">
                                  [{log.agent}]
                                </div>
                              )}
                              <div className="whitespace-pre-wrap break-words leading-tight">
                                {log.message}
                              </div>
                            </div>
                          </div>
                        )}
                      </div>
                    ))
                  )}
                  <div ref={logsEndRef} />
                </div>
              </div>

              {/* Logs Footer */}
              <div className="border-t border-gray-700 px-4 py-2 bg-gray-900/30">
                <div className="flex items-center justify-between text-xs text-gray-400">
                  <span>{agentLogs.length} eventos registrados</span>
                  <button
                    onClick={() => setAgentLogs([])}
                    className="hover:text-white transition-colors"
                  >
                    Limpar logs
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Sugestões Inteligentes - Parte Inferior */}
        <div className="mt-8">
          <div className="glass-effect rounded-xl p-6">
            <h3 className="text-white font-medium mb-4 flex items-center">
              <Lightbulb className="w-5 h-5 mr-2 text-yellow-400" />
              Sugestões Inteligentes
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
              {suggestions.map((suggestion, index) => (
                <button
                  key={index}
                  onClick={() => handleSendMessage(suggestion)}
                  disabled={isAnalyzing}
                  className="text-left p-4 bg-gray-800/30 rounded-lg hover:bg-gray-700/50 
                           transition-colors text-sm text-gray-300 hover:text-white
                           disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {suggestion}
                </button>
              ))}
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}

export default AnalysisPage