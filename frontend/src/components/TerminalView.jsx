import { useEffect, useRef } from 'react'
import { Terminal as TerminalIcon, Activity, AlertCircle, CheckCircle, Info } from 'lucide-react'

const TerminalView = ({ logs }) => {
  const terminalRef = useRef(null)

  useEffect(() => {
    if (terminalRef.current) {
      terminalRef.current.scrollTop = terminalRef.current.scrollHeight
    }
  }, [logs])

  const getLogIcon = (type) => {
    switch (type) {
      case 'success':
        return <CheckCircle className="w-4 h-4 text-green-400" />
      case 'error':
        return <AlertCircle className="w-4 h-4 text-red-400" />
      case 'warning':
        return <AlertCircle className="w-4 h-4 text-yellow-400" />
      default:
        return <Info className="w-4 h-4 text-blue-400" />
    }
  }

  const getLogColor = (type) => {
    switch (type) {
      case 'success':
        return 'text-green-300'
      case 'error':
        return 'text-red-300'
      case 'warning':
        return 'text-yellow-300'
      default:
        return 'text-blue-300'
    }
  }

  return (
    <div className="glass-effect rounded-xl overflow-hidden">
      <div className="bg-gray-900/50 px-4 py-3 border-b border-gray-700 flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <TerminalIcon className="w-5 h-5 text-instaprice-primary" />
          <h3 className="text-white font-medium">Monitor dos Robôs em Tempo Real</h3>
        </div>
        <div className="flex items-center space-x-2">
          <div className="flex space-x-1">
            <div className="w-3 h-3 bg-red-500 rounded-full"></div>
            <div className="w-3 h-3 bg-yellow-500 rounded-full"></div>
            <div className="w-3 h-3 bg-green-500 rounded-full"></div>
          </div>
          <div className="flex items-center space-x-1 text-green-400">
            <Activity className="w-4 h-4 animate-pulse" />
            <span className="text-xs">ONLINE</span>
          </div>
        </div>
      </div>
      
      <div 
        ref={terminalRef}
        className="bg-black/80 p-4 h-96 overflow-y-auto font-mono text-sm"
        style={{ 
          fontFamily: 'Monaco, Consolas, "Lucida Console", monospace',
          scrollbarWidth: 'thin',
          scrollbarColor: '#4ECDC4 transparent'
        }}
      >
        {logs.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-gray-500">
            <TerminalIcon className="w-12 h-12 mb-4 opacity-50" />
            <p className="text-center">
              Aguardando atividade dos robôs...<br />
              <span className="text-xs">Os logs aparecerão aqui em tempo real</span>
            </p>
          </div>
        ) : (
          <div className="space-y-2">
            {logs.map((log) => (
              <div key={log.id} className="flex items-start space-x-3 group">
                <span className="text-gray-500 text-xs font-mono mt-0.5 shrink-0">
                  {log.timestamp}
                </span>
                <div className="shrink-0 mt-0.5">
                  {getLogIcon(log.type)}
                </div>
                <span className={`${getLogColor(log.type)} leading-relaxed break-words`}>
                  {log.message}
                </span>
              </div>
            ))}
            
            {/* Cursor blink effect */}
            <div className="flex items-center space-x-3 mt-4">
              <span className="text-gray-500 text-xs font-mono">
                {new Date().toLocaleTimeString()}
              </span>
              <div className="shrink-0">
                <div className="w-2 h-4 bg-instaprice-primary animate-pulse"></div>
              </div>
              <span className="text-gray-400">Aguardando próxima operação...</span>
            </div>
          </div>
        )}
      </div>
      
      <div className="bg-gray-900/30 px-4 py-2 border-t border-gray-700">
        <div className="flex items-center justify-between text-xs text-gray-400">
          <span>
            {logs.length} {logs.length === 1 ? 'entrada' : 'entradas'} • 
            Última atualização: {logs.length > 0 ? logs[logs.length - 1]?.timestamp : 'N/A'}
          </span>
          <div className="flex items-center space-x-4">
            <span className="text-green-400">✓ Conectado ao backend</span>
            <button className="hover:text-white transition-colors">
              Limpar logs
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default TerminalView