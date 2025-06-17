import { useState, useEffect } from 'react'
import { 
  Settings, 
  Zap, 
  Eye, 
  EyeOff, 
  TestTube, 
  CheckCircle, 
  XCircle,
  RefreshCw,
  Copy,
  ExternalLink
} from 'lucide-react'

const ApiTest = ({ onStatusChange, onLog, onApiConfigured }) => {
  const [apiKey, setApiKey] = useState('')
  const [showApiKey, setShowApiKey] = useState(false)
  const [selectedModel, setSelectedModel] = useState('qwen-qwq-32b')
  const [testResult, setTestResult] = useState(null)
  const [testing, setTesting] = useState(false)
  const [availableModels, setAvailableModels] = useState([])

  const models = [
    // Modelos Qwen
    { id: 'qwen-qwq-32b', name: 'Qwen QWQ 32B', category: 'Qwen' },
    { id: 'qwen/qwen3-32b', name: 'Qwen 3 32B', category: 'Qwen' },
    
    // Modelos DeepSeek
    { id: 'deepseek-r1-distill-llama-70b', name: 'DeepSeek R1 Distill Llama 70B', category: 'DeepSeek' },
    
    // Modelos Google
    { id: 'gemma2-9b-it', name: 'Gemma 2 9B IT', category: 'Google' },
    
    // Modelos Compound
    { id: 'compound-beta', name: 'Compound Beta', category: 'Compound' },
    { id: 'compound-beta-mini', name: 'Compound Beta Mini', category: 'Compound' },
    
    // Modelos Llama
    { id: 'llama-3.3-70b-versatile', name: 'Llama 3.3 70B Versatile', category: 'Llama' },
    { id: 'llama-guard-3-8b', name: 'Llama Guard 3 8B', category: 'Llama' },
    { id: 'llama3-70b-8192', name: 'Llama 3 70B 8192', category: 'Llama' },
    
    // Modelos Meta Llama 4
    { id: 'meta-llama/llama-4-maverick-17b-128e-instruct', name: 'Llama 4 Maverick 17B 128E', category: 'Meta Llama 4' },
    { id: 'meta-llama/llama-4-scout-17b-16e-instruct', name: 'Llama 4 Scout 17B 16E', category: 'Meta Llama 4' },
    
    // Modelos Guard
    { id: 'meta-llama/llama-guard-4-12b', name: 'Llama Guard 4 12B', category: 'Guard' },
    { id: 'meta-llama/llama-prompt-guard-2-22m', name: 'Llama Prompt Guard 2 22M', category: 'Guard' },
    { id: 'meta-llama/llama-prompt-guard-2-86m', name: 'Llama Prompt Guard 2 86M', category: 'Guard' },
    
    // Modelos Mistral
    { id: 'mistral-saba-24b', name: 'Mistral Saba 24B', category: 'Mistral' }
  ]

  const handleApiKeyChange = (value) => {
    setApiKey(value)
    localStorage.setItem('groq_api_key', value)
  }

  const copyApiKey = () => {
    navigator.clipboard.writeText(apiKey)
    onLog('Chave API copiada para a área de transferência', 'info')
  }

  const testConnection = async () => {
    if (!apiKey.trim()) {
      setTestResult({ success: false, message: 'Chave API é obrigatória' })
      return
    }

    setTesting(true)
    onStatusChange('connecting')
    onLog('Iniciando teste de conexão com Groq...', 'info')

    try {
      // Chama a API real do backend para testar Groq
      const response = await fetch('http://localhost:8000/api/groq/test', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          apiKey: apiKey,
          model: selectedModel
        })
      })

      const result = await response.json()
      
      if (result.success) {
        setTestResult({ 
          success: true, 
          message: 'Conexão estabelecida com sucesso!',
          details: {
            endpoint: 'https://api.groq.com/openai/v1',
            model: selectedModel,
            status: 'Autenticado',
            timestamp: new Date().toLocaleString()
          }
        })
        onStatusChange('connected')
        onLog(`✅ Conexão bem-sucedida com modelo ${selectedModel}`, 'success')
        setAvailableModels(models)
        
        // Notifica o Dashboard que a API foi configurada com sucesso
        if (onApiConfigured) {
          onApiConfigured(apiKey, selectedModel)
        }
      } else {
        throw new Error(result.message || 'Falha na autenticação')
      }
    } catch (error) {
      setTestResult({ 
        success: false, 
        message: error.message || 'Erro na conexão',
        details: { error: 'Verifique sua chave API e tente novamente' }
      })
      onStatusChange('disconnected')
      onLog(`❌ Erro na conexão: ${error.message}`, 'error')
    } finally {
      setTesting(false)
    }
  }


  useEffect(() => {
    const savedKey = localStorage.getItem('groq_api_key')
    if (savedKey) {
      setApiKey(savedKey)
    }
  }, [])

  return (
    <div className="space-y-6">
      {/* API Configuration */}
      <div className="glass-effect rounded-xl p-6">
        <h3 className="text-lg font-semibold text-white mb-4 flex items-center">
          <Settings className="w-5 h-5 mr-2" />
          Configuração da API Groq
        </h3>
        
        <div className="space-y-4">
          {/* API Key Input */}
          <div className="space-y-2">
            <label className="flex items-center text-sm font-medium text-gray-300">
              <Zap className="w-4 h-4 mr-2" />
              Chave da API Groq
              <a 
                href="https://console.groq.com/keys" 
                target="_blank" 
                rel="noopener noreferrer"
                className="ml-2 text-instaprice-primary hover:text-white transition-colors"
              >
                <ExternalLink className="w-3 h-3" />
              </a>
            </label>
            <div className="relative">
              <input
                type={showApiKey ? 'text' : 'password'}
                value={apiKey}
                onChange={(e) => handleApiKeyChange(e.target.value)}
                placeholder="gsk_..."
                className="w-full px-4 py-3 bg-gray-800/50 border border-gray-600 rounded-lg 
                         text-white placeholder-gray-400 focus:outline-none focus:ring-2 
                         focus:ring-instaprice-primary focus:border-transparent transition-all pr-20"
              />
              <div className="absolute right-3 top-1/2 transform -translate-y-1/2 flex space-x-2">
                <button
                  type="button"
                  onClick={copyApiKey}
                  disabled={!apiKey}
                  className="text-gray-400 hover:text-white transition-colors disabled:opacity-30"
                >
                  <Copy className="w-4 h-4" />
                </button>
                <button
                  type="button"
                  onClick={() => setShowApiKey(!showApiKey)}
                  className="text-gray-400 hover:text-white transition-colors"
                >
                  {showApiKey ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>
            <p className="text-xs text-gray-500">
              Obtenha sua chave em: <span className="text-instaprice-primary">console.groq.com</span>
            </p>
          </div>

          {/* Model Selection */}
          <div className="space-y-2">
            <label className="text-sm font-medium text-gray-300">
              Modelo de IA
            </label>
            <select
              value={selectedModel}
              onChange={(e) => setSelectedModel(e.target.value)}
              className="w-full px-4 py-3 bg-gray-800/50 border border-gray-600 rounded-lg 
                       text-white focus:outline-none focus:ring-2 focus:ring-instaprice-primary 
                       focus:border-transparent transition-all"
            >
              {models.map(model => (
                <option key={model.id} value={model.id}>
                  {model.name}
                </option>
              ))}
            </select>
          </div>

          {/* Test Buttons */}
          <div className="space-y-3">
            <button
              onClick={testConnection}
              disabled={testing || !apiKey.trim()}
              className="w-full flex items-center justify-center space-x-2 px-4 py-3 
                       bg-gradient-to-r from-instaprice-primary to-instaprice-secondary 
                       text-white rounded-lg font-medium hover:shadow-lg 
                       hover:shadow-instaprice-primary/25 transition-all duration-300 
                       disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {testing ? (
                <>
                  <RefreshCw className="w-5 h-5 animate-spin" />
                  <span>Testando Modelo Selecionado</span>
                </>
              ) : (
                <>
                  <TestTube className="w-5 h-5" />
                  <span>Testar Modelo Selecionado</span>
                </>
              )}
            </button>

          </div>
        </div>
      </div>

      {/* Test Results */}
      {testResult && (
        <div className={`glass-effect rounded-xl p-6 border-l-4 ${
          testResult.success ? 'border-green-500' : 'border-red-500'
        }`}>
          <div className="flex items-start space-x-3">
            {testResult.success ? (
              <CheckCircle className="w-6 h-6 text-green-400 mt-0.5" />
            ) : (
              <XCircle className="w-6 h-6 text-red-400 mt-0.5" />
            )}
            <div className="flex-1">
              <h4 className={`font-medium ${
                testResult.success ? 'text-green-300' : 'text-red-300'
              }`}>
                {testResult.success ? 'Conexão Bem-sucedida' : 'Falha na Conexão'}
              </h4>
              <p className="text-gray-300 mt-1">{testResult.message}</p>
              
              {testResult.details && (
                <div className="mt-4 space-y-2">
                  {Object.entries(testResult.details).map(([key, value]) => (
                    <div key={key} className="flex justify-between text-sm">
                      <span className="text-gray-400 capitalize">{key.replace(/([A-Z])/g, ' $1')}:</span>
                      <span className="text-white font-mono">{value}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Available Models */}
      {availableModels.length > 0 && (
        <div className="glass-effect rounded-xl p-6">
          <h4 className="font-medium text-white mb-4">
            Resultados dos Testes ({availableModels.filter(m => m.status === 'success').length}/{availableModels.length} disponíveis)
          </h4>
          
          {/* Group by category */}
          {Object.entries(
            availableModels.reduce((acc, model) => {
              const category = model.category || 'Outros'
              if (!acc[category]) acc[category] = []
              acc[category].push(model)
              return acc
            }, {})
          ).map(([category, categoryModels]) => (
            <div key={category} className="mb-6 last:mb-0">
              <h5 className="text-gray-300 font-medium mb-3 text-sm">{category}</h5>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {categoryModels.map(model => (
                  <div 
                    key={model.id}
                    className={`p-3 rounded-lg border transition-all cursor-pointer ${
                      model.status === 'success' 
                        ? selectedModel === model.id 
                          ? 'border-instaprice-primary bg-instaprice-primary/10' 
                          : 'border-green-500/30 bg-green-500/5 hover:bg-green-500/10'
                        : 'border-red-500/30 bg-red-500/5'
                    }`}
                    onClick={() => model.status === 'success' && setSelectedModel(model.id)}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center space-x-2">
                          <span className="text-white text-sm font-medium">{model.name}</span>
                          {model.status === 'success' ? (
                            <CheckCircle className="w-4 h-4 text-green-400" />
                          ) : (
                            <XCircle className="w-4 h-4 text-red-400" />
                          )}
                        </div>
                        {model.status === 'error' && model.error && (
                          <p className="text-red-300 text-xs mt-1">{model.error}</p>
                        )}
                      </div>
                      {selectedModel === model.id && model.status === 'success' && (
                        <div className="w-2 h-2 bg-instaprice-primary rounded-full"></div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default ApiTest