import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { 
  Upload, 
  Settings, 
  Download, 
  Activity, 
  Zap, 
  FileText, 
  Terminal,
  LogOut,
  CheckCircle,
  XCircle,
  Clock,
  Users,
  HelpCircle
} from 'lucide-react'
import FileUpload from '../components/FileUpload'
import TerminalView from '../components/TerminalView'
import ApiTest from '../components/ApiTest'
import { filesAPI } from '../services/api'
import { wsManager } from '../utils/websocket'
import instaprice from '../assets/instaprice.png'

const Dashboard = ({ user }) => {
  const [activeTab, setActiveTab] = useState('api')
  const [connectionStatus, setConnectionStatus] = useState('disconnected')
  const [processingFiles, setProcessingFiles] = useState([])
  const [logs, setLogs] = useState([])
  const [configuredApiKey, setConfiguredApiKey] = useState('')
  const [configuredModel, setConfiguredModel] = useState('')
  const navigate = useNavigate()

  useEffect(() => {
    // Conecta WebSocket para logs em tempo real
    wsManager.connect('ws://localhost:8000/ws')
    
    // Listeners para WebSocket
    wsManager.on('connected', (isConnected) => {
      setConnectionStatus(isConnected ? 'connected' : 'disconnected')
      if (isConnected) {
        addLog('🔗 Conectado ao servidor Instaprice', 'success')
      }
    })

    wsManager.on('log', (data) => {
      addLog(data.message, data.level)
    })

    wsManager.on('file_uploaded', (data) => {
      addLog(`📁 Arquivo recebido: ${data.data.filename}`, 'success')
    })

    wsManager.on('processing_started', (data) => {
      addLog(`🤖 Iniciando análise: ${data.data.file_id}`, 'info')
    })

    wsManager.on('processing_completed', (data) => {
      addLog(`✅ Análise concluída: ${data.data.file_id}`, 'success')
    })

    // Cleanup on unmount
    return () => {
      wsManager.disconnect()
    }
  }, [])

  const handleLogout = () => {
    navigate('/')
  }

  const addLog = (message, type = 'info') => {
    const newLog = {
      id: Date.now(),
      message,
      type,
      timestamp: new Date().toLocaleTimeString()
    }
    setLogs(prev => [...prev, newLog])
  }

  const handleApiConfigured = (apiKey, model) => {
    console.log('Dashboard: API configurada com sucesso:', { apiKey: '***', model })
    setConfiguredApiKey(apiKey)
    setConfiguredModel(model)
    addLog(`🔑 API configurada: ${model}`, 'success')
  }

  const handleFileUpload = async (files) => {
    console.log('Dashboard: handleFileUpload chamado com:', files)
    addLog(`🎯 Dashboard recebeu ${files.length} arquivo(s)`, 'info')
    
    files.forEach(async file => {
      console.log('Dashboard: Processando arquivo:', file)
      if (file.serverResponse) {
        // Arquivo já foi enviado, agora adiciona à lista
        const fileData = {
          id: file.id || file.serverResponse.file_id,
          name: file.name,
          size: file.size,
          status: 'ready',
          progress: 100,
          serverFileId: file.serverResponse.file_id,
          path: `/uploads/${file.serverResponse.file_id}`,
          timestamp: new Date().toLocaleString()
        }
        
        console.log('Dashboard: Adicionando arquivo à lista:', fileData)
        setProcessingFiles(prev => {
          const newList = [...prev, fileData]
          console.log('Dashboard: Nova lista de arquivos:', newList)
          return newList
        })
        
        addLog(`📁 Arquivo ${file.name} pronto para análise!`, 'success')
      }
    })
  }

  const StatusBadge = ({ status }) => {
    const statusConfig = {
      connected: { color: 'bg-green-500', text: 'Conectado', icon: CheckCircle },
      disconnected: { color: 'bg-red-500', text: 'Desconectado', icon: XCircle },
      connecting: { color: 'bg-yellow-500', text: 'Conectando...', icon: Clock }
    }
    
    const config = statusConfig[status]
    const Icon = config.icon
    
    return (
      <div className="flex items-center space-x-2">
        <div className={`w-2 h-2 rounded-full ${config.color} animate-pulse`}></div>
        <Icon className="w-4 h-4" />
        <span className="text-sm">{config.text}</span>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-instaprice-darker to-instaprice-dark">
      {/* Header */}
      <header className="bg-black/20 backdrop-blur-md border-b border-gray-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-4">
              <img src={instaprice} alt="Instaprice" className="h-16" />
              <div>
                <h1 className="text-xl font-bold text-white">Instaprice - Análise de Notas Fiscais</h1>
                <p className="text-sm text-gray-400">
                  Bem-vindo, {user?.username} ({user?.type})
                </p>
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              <StatusBadge status={connectionStatus} />
              <button
                onClick={handleLogout}
                className="flex items-center space-x-2 px-4 py-2 bg-red-600/20 
                         border border-red-500/30 rounded-lg hover:bg-red-600/30 
                         transition-colors text-red-400 hover:text-red-300"
              >
                <LogOut className="w-4 h-4" />
                <span>Sair</span>
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Quick Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="glass-effect rounded-xl p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-400">Arquivos Processados</p>
                <p className="text-2xl font-bold text-white">{processingFiles.filter(f => f.status === 'completed').length}</p>
              </div>
              <FileText className="w-8 h-8 text-instaprice-primary" />
            </div>
          </div>
          
          <div className="glass-effect rounded-xl p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-400">Em Processamento</p>
                <p className="text-2xl font-bold text-white">{processingFiles.filter(f => f.status === 'processing').length}</p>
              </div>
              <Activity className="w-8 h-8 text-yellow-500" />
            </div>
          </div>
          
          <div className="glass-effect rounded-xl p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-400">Modelos Disponíveis</p>
                <p className="text-2xl font-bold text-white">5</p>
              </div>
              <Zap className="w-8 h-8 text-blue-500" />
            </div>
          </div>
          
          <div className="glass-effect rounded-xl p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-400">Relatórios</p>
                <p className="text-2xl font-bold text-white">3</p>
              </div>
              <Download className="w-8 h-8 text-green-500" />
            </div>
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="flex space-x-1 mb-6 bg-gray-800/30 p-1 rounded-lg">
          <button
            onClick={() => setActiveTab('api')}
            className={`flex items-center space-x-2 px-4 py-2 rounded-md transition-all ${
              activeTab === 'api' 
                ? 'bg-instaprice-primary text-white' 
                : 'text-gray-400 hover:text-white'
            }`}
          >
            <Settings className="w-4 h-4" />
            <span>Configuração API</span>
          </button>
          
          <button
            onClick={() => setActiveTab('upload')}
            className={`flex items-center space-x-2 px-4 py-2 rounded-md transition-all ${
              activeTab === 'upload' 
                ? 'bg-instaprice-primary text-white' 
                : 'text-gray-400 hover:text-white'
            }`}
          >
            <Upload className="w-4 h-4" />
            <span>Upload de Arquivos</span>
          </button>
          
          <button
            onClick={() => setActiveTab('terminal')}
            className={`flex items-center space-x-2 px-4 py-2 rounded-md transition-all ${
              activeTab === 'terminal' 
                ? 'bg-instaprice-primary text-white' 
                : 'text-gray-400 hover:text-white'
            }`}
          >
            <Terminal className="w-4 h-4" />
            <span>Monitor dos Robôs</span>
          </button>
          
          <button
            onClick={() => setActiveTab('about')}
            className={`flex items-center space-x-2 px-4 py-2 rounded-md transition-all ${
              activeTab === 'about' 
                ? 'bg-instaprice-primary text-white' 
                : 'text-gray-400 hover:text-white'
            }`}
          >
            <Users className="w-4 h-4" />
            <span>Sobre Nós</span>
          </button>
          
          <button
            onClick={() => setActiveTab('help')}
            className={`flex items-center space-x-2 px-4 py-2 rounded-md transition-all ${
              activeTab === 'help' 
                ? 'bg-instaprice-primary text-white' 
                : 'text-gray-400 hover:text-white'
            }`}
          >
            <HelpCircle className="w-4 h-4" />
            <span>Ajuda</span>
          </button>
        </div>

        {/* Tab Content */}
        <div className="space-y-6">
          {activeTab === 'upload' && (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <FileUpload onFileUpload={handleFileUpload} onLog={addLog} />
              
              <div className="glass-effect rounded-xl p-6">
                <h3 className="text-lg font-semibold text-white mb-4">Arquivos a Processar</h3>
                <div className="space-y-3">
                  {processingFiles.length === 0 ? (
                    <p className="text-gray-400 text-center py-8">
                      Nenhum arquivo para processar
                    </p>
                  ) : (
                    processingFiles.map(file => (
                      <div key={file.id} className="bg-gray-800/50 rounded-lg p-4">
                        <div className="flex items-center justify-between mb-2">
                          <div className="flex-1">
                            <div className="text-white text-sm font-medium mb-1">{file.name}</div>
                            <div className="text-gray-400 text-xs font-mono">
                              Caminho: {file.path || '/uploads/' + file.serverFileId}
                            </div>
                            {file.timestamp && (
                              <div className="text-gray-500 text-xs mt-1">
                                Carregado em: {file.timestamp}
                              </div>
                            )}
                          </div>
                          <span className={`text-xs px-2 py-1 rounded ml-3 ${
                            file.status === 'completed' ? 'bg-green-600 text-green-100' :
                            file.status === 'processing' ? 'bg-yellow-600 text-yellow-100' :
                            file.status === 'ready' ? 'bg-blue-600 text-blue-100' :
                            'bg-gray-600 text-gray-100'
                          }`}>
                            {file.status === 'completed' ? 'Concluído' : 
                             file.status === 'processing' ? 'Processando' : 
                             file.status === 'ready' ? 'Pronto' : 'Pendente'}
                          </span>
                        </div>
                        <div className="w-full bg-gray-700 rounded-full h-2">
                          <div 
                            className="bg-instaprice-primary h-2 rounded-full transition-all duration-300"
                            style={{ width: `${file.progress}%` }}
                          ></div>
                        </div>
                        <div className="flex justify-between items-center text-xs text-gray-400 mt-2">
                          <div>
                            <span>Tamanho: {(file.size / 1024).toFixed(1)} KB</span>
                            <span className="ml-4">Progresso: {file.progress}%</span>
                          </div>
                          {file.status === 'ready' && (
                            <button
                              onClick={() => {
                                if (!configuredApiKey || !configuredModel) {
                                  addLog('❌ Configure a API primeiro na aba "Configuração da API"', 'error')
                                  setActiveTab('api')
                                  return
                                }
                                // Salva dados no localStorage para a página de análise
                                localStorage.setItem('analysisData', JSON.stringify({
                                  file: file,
                                  apiKey: configuredApiKey,
                                  model: configuredModel,
                                  timestamp: new Date().toISOString()
                                }))
                                navigate('/analyze')
                              }}
                              className="px-3 py-1 bg-instaprice-primary text-white text-xs rounded-md hover:bg-instaprice-secondary transition-colors"
                            >
                              Analisar
                            </button>
                          )}
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </div>
            </div>
          )}

          {activeTab === 'terminal' && (
            <TerminalView logs={logs} />
          )}

          {activeTab === 'api' && (
            <ApiTest 
              onStatusChange={setConnectionStatus}
              onLog={addLog}
              onApiConfigured={handleApiConfigured}
            />
          )}

          {activeTab === 'about' && (
            <div className="glass-effect rounded-xl p-8">
              <div className="max-w-4xl mx-auto">
                <h2 className="text-3xl font-bold text-white mb-6 text-center">
                  🎯 Sobre Nós - Grupo 9
                </h2>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">
                  <div className="space-y-4">
                    <h3 className="text-xl font-semibold text-instaprice-primary flex items-center">
                      <Users className="w-6 h-6 mr-2" />
                      Nossa Equipe
                    </h3>
                    <p className="text-gray-300 leading-relaxed">
                      Somos o <strong className="text-white">Grupo 9</strong> do desafio <strong className="text-instaprice-primary">I2A2 - Agentes Inteligentes</strong>, 
                      uma equipe multidisciplinar apaixonada por inovação e tecnologia. Unidos pela visão de revolucionar 
                      a análise de documentos fiscais através da inteligência artificial.
                    </p>
                    
                    <div className="bg-gray-800/50 rounded-lg p-4">
                      <h4 className="text-lg font-medium text-white mb-3">👥 Integrantes do Grupo 9:</h4>
                      <ul className="space-y-3 text-gray-300">
                        <li className="flex items-center justify-between">
                          <div className="flex items-center">
                            <span className="w-2 h-2 bg-instaprice-primary rounded-full mr-3"></span>
                            <strong>Daniele</strong>
                          </div>
                          <span className="text-sm text-gray-400">daniele_mkt@hotmail.com</span>
                        </li>
                        <li className="flex items-center justify-between">
                          <div className="flex items-center">
                            <span className="w-2 h-2 bg-instaprice-primary rounded-full mr-3"></span>
                            <strong>Erico</strong>
                          </div>
                          <span className="text-sm text-gray-400">erico@e-reis.com</span>
                        </li>
                        <li className="flex items-center justify-between">
                          <div className="flex items-center">
                            <span className="w-2 h-2 bg-instaprice-primary rounded-full mr-3"></span>
                            <strong>Erike</strong>
                          </div>
                          <span className="text-sm text-gray-400">erike.axel@gmail.com</span>
                        </li>
                        <li className="flex items-center justify-between">
                          <div className="flex items-center">
                            <span className="w-2 h-2 bg-instaprice-primary rounded-full mr-3"></span>
                            <strong>Gleison</strong>
                          </div>
                          <span className="text-sm text-gray-400">eng.gleison@gmail.com</span>
                        </li>
                        <li className="flex items-center justify-between">
                          <div className="flex items-center">
                            <span className="w-2 h-2 bg-instaprice-primary rounded-full mr-3"></span>
                            <strong>Gustavo</strong>
                          </div>
                          <span className="text-sm text-gray-400">gustavoascalderon@gmail.com</span>
                        </li>
                        <li className="flex items-center justify-between bg-gradient-to-r from-instaprice-primary/10 to-instaprice-secondary/10 rounded-lg p-2 border border-instaprice-primary/20">
                          <div className="flex items-center">
                            <span className="w-2 h-2 bg-instaprice-primary rounded-full mr-3 animate-pulse"></span>
                            <div>
                              <strong className="text-white">Juliana</strong>
                              <span className="ml-2 text-xs bg-instaprice-primary text-white px-2 py-0.5 rounded-full">Responsável</span>
                            </div>
                          </div>
                          <span className="text-sm text-instaprice-primary font-medium">juliana.coelho@live.com</span>
                        </li>
                      </ul>
                    </div>
                  </div>

                  <div className="space-y-4">
                    <h3 className="text-xl font-semibold text-instaprice-primary flex items-center">
                      <Zap className="w-6 h-6 mr-2" />
                      Nossa Missão
                    </h3>
                    <p className="text-gray-300 leading-relaxed">
                      Desenvolver soluções inteligentes que simplifiquem e automatizem processos complexos. 
                      Com o Instaprice, buscamos democratizar o acesso à análise avançada de dados fiscais, 
                      tornando-a acessível e intuitiva para todos.
                    </p>

                    <div className="bg-gradient-to-r from-instaprice-primary/10 to-instaprice-secondary/10 rounded-lg p-4 border border-instaprice-primary/20">
                      <h4 className="text-lg font-medium text-white mb-3">🏆 Nossos Valores:</h4>
                      <ul className="space-y-2 text-gray-300">
                        <li><strong>Inovação:</strong> Sempre buscando novas formas de resolver problemas</li>
                        <li><strong>Qualidade:</strong> Código limpo, testes rigorosos e documentação clara</li>
                        <li><strong>Colaboração:</strong> Trabalho em equipe e conhecimento compartilhado</li>
                        <li><strong>Impacto:</strong> Soluções que realmente fazem a diferença</li>
                      </ul>
                    </div>
                  </div>
                </div>

                <div className="bg-gray-800/30 rounded-lg p-6 text-center">
                  <h3 className="text-xl font-semibold text-white mb-3">
                    🚀 Desafio I2A2 - Agentes Inteligentes
                  </h3>
                  <p className="text-gray-300 leading-relaxed">
                    Este projeto nasceu do desafio de criar um sistema multiagente capaz de processar e analisar 
                    documentos fiscais de forma autônoma e inteligente. Utilizando as mais modernas tecnologias 
                    como CrewAI, RAG e modelos de linguagem avançados, o Instaprice representa nossa contribuição 
                    para o futuro da automação fiscal.
                  </p>
                  <div className="mt-4 flex justify-center space-x-4 text-sm text-gray-400">
                    <span>📅 2025</span>
                    <span>•</span>
                    <span>🥇 Grupo 9</span>
                    <span>•</span>
                    <span>🤖 I2A2 Challenge</span>
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'help' && (
            <div className="glass-effect rounded-xl p-8">
              <div className="max-w-6xl mx-auto">
                <h2 className="text-3xl font-bold text-white mb-8 text-center">
                  📖 Central de Ajuda - Instaprice
                </h2>
                
                {/* Quick Start destacado */}
                <div className="mb-10">
                  <div className="bg-gradient-to-r from-instaprice-primary/20 to-instaprice-secondary/20 rounded-xl p-8 border border-instaprice-primary/30">
                    <h3 className="text-2xl font-bold text-white mb-6 text-center">
                      🚀 Início Rápido
                    </h3>
                    <div className="grid grid-cols-1 md:grid-cols-6 gap-3">
                      <div className="bg-white/10 backdrop-blur rounded-lg p-4 text-center transform hover:scale-105 transition-transform">
                        <div className="bg-instaprice-primary text-white rounded-full w-10 h-10 flex items-center justify-center text-sm font-bold mx-auto mb-2">1</div>
                        <h4 className="text-white font-semibold mb-1 text-sm">Configure API</h4>
                        <p className="text-gray-300 text-xs">Adicione sua chave Groq</p>
                      </div>
                      <div className="bg-white/10 backdrop-blur rounded-lg p-4 text-center transform hover:scale-105 transition-transform">
                        <div className="bg-instaprice-primary text-white rounded-full w-10 h-10 flex items-center justify-center text-sm font-bold mx-auto mb-2">2</div>
                        <h4 className="text-white font-semibold mb-1 text-sm">Upload ZIP</h4>
                        <p className="text-gray-300 text-xs">Envie suas notas fiscais</p>
                      </div>
                      <div className="bg-white/10 backdrop-blur rounded-lg p-4 text-center transform hover:scale-105 transition-transform">
                        <div className="bg-instaprice-primary text-white rounded-full w-10 h-10 flex items-center justify-center text-sm font-bold mx-auto mb-2">3</div>
                        <h4 className="text-white font-semibold mb-1 text-sm">Pergunte</h4>
                        <p className="text-gray-300 text-xs">Use linguagem natural</p>
                      </div>
                      <div className="bg-white/10 backdrop-blur rounded-lg p-4 text-center transform hover:scale-105 transition-transform">
                        <div className="bg-instaprice-primary text-white rounded-full w-10 h-10 flex items-center justify-center text-sm font-bold mx-auto mb-2">4</div>
                        <h4 className="text-white font-semibold mb-1 text-sm">Monitore</h4>
                        <p className="text-gray-300 text-xs">Acompanhe o processamento</p>
                      </div>
                      <div className="bg-white/10 backdrop-blur rounded-lg p-4 text-center transform hover:scale-105 transition-transform">
                        <div className="bg-instaprice-primary text-white rounded-full w-10 h-10 flex items-center justify-center text-sm font-bold mx-auto mb-2">5</div>
                        <h4 className="text-white font-semibold mb-1 text-sm">Receba Resposta</h4>
                        <p className="text-gray-300 text-xs">Análise automatizada</p>
                      </div>
                      <div className="bg-white/10 backdrop-blur rounded-lg p-4 text-center transform hover:scale-105 transition-transform">
                        <div className="bg-instaprice-primary text-white rounded-full w-10 h-10 flex items-center justify-center text-sm font-bold mx-auto mb-2">6</div>
                        <h4 className="text-white font-semibold mb-1 text-sm">Insights</h4>
                        <p className="text-gray-300 text-xs">Relatórios inteligentes</p>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Conteúdo principal em grid */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                  {/* Coluna esquerda - Informações principais */}
                  <div className="space-y-6">
                    {/* O que é */}
                    <div className="bg-gray-800/50 rounded-lg p-6">
                      <h3 className="text-xl font-semibold text-instaprice-primary mb-4">
                        📊 Sobre o Instaprice
                      </h3>
                      <p className="text-gray-300 leading-relaxed mb-4">
                        Sistema inteligente para análise automatizada de notas fiscais eletrônicas, 
                        utilizando agentes de IA especializados para processar, validar e gerar insights 
                        a partir de documentos fiscais.
                      </p>
                      <div className="bg-blue-600/10 border border-blue-500/30 rounded-lg p-4">
                        <p className="text-blue-300">
                          <strong>💡 Powered by:</strong> CrewAI + Groq API + FastAPI
                        </p>
                      </div>
                    </div>

                    {/* Como funciona */}
                    <div className="bg-gray-800/50 rounded-lg p-6">
                      <h3 className="text-xl font-semibold text-instaprice-primary mb-4">
                        ⚙️ Como Funciona
                      </h3>
                      <div className="space-y-4">
                        <div className="flex items-start space-x-3">
                          <span className="text-instaprice-primary font-bold">1.</span>
                          <div>
                            <h4 className="text-white font-medium">Upload do arquivo</h4>
                            <p className="text-gray-400 text-sm">Envie um ZIP com CSVs de notas fiscais</p>
                          </div>
                        </div>
                        <div className="flex items-start space-x-3">
                          <span className="text-instaprice-primary font-bold">2.</span>
                          <div>
                            <h4 className="text-white font-medium">Processamento inteligente</h4>
                            <p className="text-gray-400 text-sm">7 agentes especializados analisam os dados</p>
                          </div>
                        </div>
                        <div className="flex items-start space-x-3">
                          <span className="text-instaprice-primary font-bold">3.</span>
                          <div>
                            <h4 className="text-white font-medium">Faça perguntas</h4>
                            <p className="text-gray-400 text-sm">Use linguagem natural para consultar</p>
                          </div>
                        </div>
                        <div className="flex items-start space-x-3">
                          <span className="text-instaprice-primary font-bold">4.</span>
                          <div>
                            <h4 className="text-white font-medium">Resposta final eloquente</h4>
                            <p className="text-gray-400 text-sm">O Porta-Voz Eloquente consolida todas as informações em uma resposta magistral</p>
                          </div>
                        </div>
                      </div>
                    </div>

                    {/* Exemplos práticos */}
                    <div className="bg-gray-800/50 rounded-lg p-6">
                      <h3 className="text-xl font-semibold text-instaprice-primary mb-4">
                        💬 Exemplos de Perguntas
                      </h3>
                      <div className="space-y-3">
                        <div className="bg-gray-700/50 rounded-lg p-3">
                          <p className="text-white text-sm">📊 "Qual o total de vendas em janeiro?"</p>
                        </div>
                        <div className="bg-gray-700/50 rounded-lg p-3">
                          <p className="text-white text-sm">🏢 "Mostre os 5 maiores compradores"</p>
                        </div>
                        <div className="bg-gray-700/50 rounded-lg p-3">
                          <p className="text-white text-sm">📦 "Quais produtos mais venderam?"</p>
                        </div>
                        <div className="bg-gray-700/50 rounded-lg p-3">
                          <p className="text-white text-sm">📍 "Compare vendas por estado"</p>
                        </div>
                        <div className="bg-gray-700/50 rounded-lg p-3">
                          <p className="text-white text-sm">📈 "Análise de tendências mensais"</p>
                        </div>
                      </div>
                    </div>

                    {/* Fluxo de trabalho dos agentes */}
                    <div className="bg-gray-800/50 rounded-lg p-6">
                      <h3 className="text-xl font-semibold text-instaprice-primary mb-4">
                        🔄 Fluxo dos Agentes
                      </h3>
                      <div className="space-y-3">
                        <div className="flex items-center space-x-3 p-2 bg-gray-700/30 rounded">
                          <span className="text-xs bg-instaprice-primary text-white px-2 py-1 rounded">1</span>
                          <div className="text-xs">
                            <span className="text-white font-medium">🗂️ Zip Desbravador</span>
                            <span className="text-gray-400 ml-2">→ Extrai CSVs</span>
                          </div>
                        </div>
                        <div className="flex items-center space-x-3 p-2 bg-gray-700/30 rounded">
                          <span className="text-xs bg-instaprice-primary text-white px-2 py-1 rounded">2</span>
                          <div className="text-xs">
                            <span className="text-white font-medium">🛡️ Guardião Pydantic</span>
                            <span className="text-gray-400 ml-2">→ Valida dados</span>
                          </div>
                        </div>
                        <div className="flex items-center space-x-3 p-2 bg-gray-700/30 rounded">
                          <span className="text-xs bg-instaprice-primary text-white px-2 py-1 rounded">3</span>
                          <div className="text-xs">
                            <span className="text-white font-medium">🧠 Linguista Lúcido</span>
                            <span className="text-gray-400 ml-2">→ Interpreta pergunta</span>
                          </div>
                        </div>
                        <div className="flex items-center space-x-3 p-2 bg-gray-700/30 rounded">
                          <span className="text-xs bg-instaprice-primary text-white px-2 py-1 rounded">4</span>
                          <div className="text-xs">
                            <span className="text-white font-medium">📊 Executor</span>
                            <span className="text-gray-400 ml-2">→ Executa consultas</span>
                          </div>
                        </div>
                        <div className="flex items-center space-x-3 p-2 bg-gray-700/30 rounded">
                          <span className="text-xs bg-instaprice-primary text-white px-2 py-1 rounded">5</span>
                          <div className="text-xs">
                            <span className="text-white font-medium">🎭 RP Lúdico</span>
                            <span className="text-gray-400 ml-2">→ Humaniza resposta</span>
                          </div>
                        </div>
                        <div className="flex items-center space-x-3 p-2 bg-gray-700/30 rounded">
                          <span className="text-xs bg-instaprice-primary text-white px-2 py-1 rounded">6</span>
                          <div className="text-xs">
                            <span className="text-white font-medium">💡 Sugestor</span>
                            <span className="text-gray-400 ml-2">→ Gera sugestões</span>
                          </div>
                        </div>
                        <div className="flex items-center space-x-3 p-2 bg-gradient-to-r from-instaprice-primary/20 to-instaprice-secondary/20 rounded border border-instaprice-primary/30">
                          <span className="text-xs bg-instaprice-primary text-white px-2 py-1 rounded">7</span>
                          <div className="text-xs">
                            <span className="text-white font-medium">🎩 Porta-Voz Eloquente</span>
                            <span className="text-instaprice-primary ml-2">→ Resposta final magistral</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Coluna direita - Detalhes técnicos */}
                  <div className="space-y-6">
                    {/* Agentes */}
                    <div className="bg-gray-800/50 rounded-lg p-6">
                      <h3 className="text-xl font-semibold text-instaprice-primary mb-4">
                        🤖 Agentes Inteligentes
                      </h3>
                      <div className="grid grid-cols-2 gap-3">
                        <div className="bg-gray-700/50 rounded-lg p-3">
                          <h4 className="text-white font-medium text-sm mb-1">🗂️ Zip Desbravador</h4>
                          <p className="text-gray-400 text-xs">Extrai arquivos comprimidos</p>
                        </div>
                        <div className="bg-gray-700/50 rounded-lg p-3">
                          <h4 className="text-white font-medium text-sm mb-1">🛡️ Guardião Pydantic</h4>
                          <p className="text-gray-400 text-xs">Valida dados dos CSVs</p>
                        </div>
                        <div className="bg-gray-700/50 rounded-lg p-3">
                          <h4 className="text-white font-medium text-sm mb-1">🧠 Linguista Lúcido</h4>
                          <p className="text-gray-400 text-xs">Interpreta perguntas</p>
                        </div>
                        <div className="bg-gray-700/50 rounded-lg p-3">
                          <h4 className="text-white font-medium text-sm mb-1">📊 Executor de Consultas</h4>
                          <p className="text-gray-400 text-xs">Executa análises Pandas</p>
                        </div>
                        <div className="bg-gray-700/50 rounded-lg p-3">
                          <h4 className="text-white font-medium text-sm mb-1">🎭 RP Lúdico</h4>
                          <p className="text-gray-400 text-xs">Humaniza respostas</p>
                        </div>
                        <div className="bg-gray-700/50 rounded-lg p-3">
                          <h4 className="text-white font-medium text-sm mb-1">💡 Sugestor Visionário</h4>
                          <p className="text-gray-400 text-xs">Gera sugestões inteligentes</p>
                        </div>
                        <div className="bg-gradient-to-r from-instaprice-primary/20 to-instaprice-secondary/20 rounded-lg p-3 border border-instaprice-primary/30 col-span-2">
                          <h4 className="text-white font-medium text-sm mb-1">🎩 Porta-Voz Eloquente</h4>
                          <p className="text-instaprice-primary text-xs">Agente final que consolida todas as respostas dos outros agentes em uma resposta magistral e definitiva ao usuário</p>
                        </div>
                      </div>
                    </div>

                    {/* Configuração API */}
                    <div className="bg-gray-800/50 rounded-lg p-6">
                      <h3 className="text-xl font-semibold text-instaprice-primary mb-4">
                        🔧 Configuração da API
                      </h3>
                      <div className="space-y-3">
                        <div className="bg-gray-700/50 rounded-lg p-4">
                          <h4 className="text-white font-medium mb-2">Obter chave Groq:</h4>
                          <ol className="text-gray-300 text-sm space-y-1">
                            <li>1. Acesse console.groq.com</li>
                            <li>2. Crie uma conta gratuita</li>
                            <li>3. Gere sua API key</li>
                            <li>4. Cole na aba Configuração API</li>
                          </ol>
                        </div>
                        <div className="bg-blue-600/10 border border-blue-500/30 rounded-lg p-3">
                          <p className="text-blue-300 text-sm">
                            <strong>💡 Dica:</strong> Teste a conexão antes de fazer upload
                          </p>
                        </div>
                      </div>
                    </div>

                    {/* Stack técnica */}
                    <div className="bg-gray-800/50 rounded-lg p-6">
                      <h3 className="text-xl font-semibold text-instaprice-primary mb-4">
                        🛠️ Tecnologias Utilizadas
                      </h3>
                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <h4 className="text-white font-medium mb-2 text-sm">Backend:</h4>
                          <div className="space-y-1">
                            <p className="text-gray-300 text-xs flex items-center">
                              <span className="w-2 h-2 bg-green-500 rounded-full mr-2"></span>
                              CrewAI Framework
                            </p>
                            <p className="text-gray-300 text-xs flex items-center">
                              <span className="w-2 h-2 bg-red-500 rounded-full mr-2"></span>
                              Pydantic
                            </p>
                            <p className="text-gray-300 text-xs flex items-center">
                              <span className="w-2 h-2 bg-blue-500 rounded-full mr-2"></span>
                              FastAPI
                            </p>
                            <p className="text-gray-300 text-xs flex items-center">
                              <span className="w-2 h-2 bg-purple-500 rounded-full mr-2"></span>
                              Groq LLM
                            </p>
                            <p className="text-gray-300 text-xs flex items-center">
                              <span className="w-2 h-2 bg-orange-500 rounded-full mr-2"></span>
                              Pandas
                            </p>
                          </div>
                        </div>
                        <div>
                          <h4 className="text-white font-medium mb-2 text-sm">Frontend:</h4>
                          <div className="space-y-1">
                            <p className="text-gray-300 text-xs flex items-center">
                              <span className="w-2 h-2 bg-blue-400 rounded-full mr-2"></span>
                              React 19
                            </p>
                            <p className="text-gray-300 text-xs flex items-center">
                              <span className="w-2 h-2 bg-teal-500 rounded-full mr-2"></span>
                              Tailwind CSS
                            </p>
                            <p className="text-gray-300 text-xs flex items-center">
                              <span className="w-2 h-2 bg-purple-400 rounded-full mr-2"></span>
                              Vite
                            </p>
                            <p className="text-gray-300 text-xs flex items-center">
                              <span className="w-2 h-2 bg-green-400 rounded-full mr-2"></span>
                              WebSocket
                            </p>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Seções complementares em grid */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-8">
                  {/* Monitoramento */}
                  <div className="bg-gray-800/50 rounded-lg p-6">
                    <h3 className="text-lg font-semibold text-instaprice-primary mb-3">
                      🔄 Monitoramento
                    </h3>
                    <div className="space-y-2 text-sm">
                      <div className="flex items-center space-x-2">
                        <span className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></span>
                        <span className="text-gray-300">WebSocket ativo</span>
                      </div>
                      <div className="flex items-center space-x-2">
                        <span className="w-3 h-3 bg-blue-500 rounded-full"></span>
                        <span className="text-gray-300">Logs em tempo real</span>
                      </div>
                      <div className="flex items-center space-x-2">
                        <span className="w-3 h-3 bg-purple-500 rounded-full"></span>
                        <span className="text-gray-300">Status detalhado</span>
                      </div>
                    </div>
                  </div>

                  {/* Interface */}
                  <div className="bg-gray-800/50 rounded-lg p-6">
                    <h3 className="text-lg font-semibold text-instaprice-primary mb-3">
                      📱 Interface
                    </h3>
                    <div className="space-y-2 text-sm">
                      <p className="text-gray-300">✨ Design moderno</p>
                      <p className="text-gray-300">🎯 Foco em UX</p>
                      <p className="text-gray-300">📲 Responsivo</p>
                    </div>
                  </div>

                  {/* Segurança */}
                  <div className="bg-gradient-to-r from-instaprice-primary/10 to-instaprice-secondary/10 rounded-lg p-6 border border-instaprice-primary/20">
                    <h3 className="text-lg font-semibold text-white mb-3">
                      🛡️ Segurança
                    </h3>
                    <div className="space-y-2 text-sm">
                      <p className="text-gray-300">✅ Validação rigorosa</p>
                      <p className="text-gray-300">✅ Dados protegidos</p>
                      <p className="text-gray-300">✅ API segura</p>
                    </div>
                  </div>
                </div>

                {/* Rodapé da ajuda */}
                <div className="mt-8 text-center">
                  <div className="bg-gray-800/30 rounded-lg p-4">
                    <p className="text-gray-400 text-sm">
                      Precisa de mais ajuda? Entre em contato com o Grupo 9 do desafio I2A2
                    </p>
                    <p className="text-instaprice-primary text-xs mt-2">
                      Instaprice v1.0 - Sistema Inteligente de Análise Fiscal
                    </p>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Actions */}
        <div className="mt-8 flex justify-center space-x-4">
          <button
            onClick={() => navigate('/analyze')}
            className="flex items-center space-x-2 px-6 py-3 bg-gradient-to-r 
                     from-instaprice-primary to-instaprice-secondary text-white rounded-lg 
                     font-medium hover:shadow-lg hover:shadow-instaprice-primary/25 
                     transition-all duration-300"
          >
            <Activity className="w-5 h-5" />
            <span>Fazer Análise Inteligente</span>
          </button>
          
          <button className="flex items-center space-x-2 px-6 py-3 bg-gray-700 
                           text-white rounded-lg font-medium hover:bg-gray-600 
                           transition-colors">
            <Download className="w-5 h-5" />
            <span>Baixar Relatórios</span>
          </button>
        </div>
      </main>
    </div>
  )
}

export default Dashboard