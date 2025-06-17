/**
 * Configurações de timeout para diferentes operações
 * Centralizadas para fácil ajuste
 */

export const TIMEOUTS = {
  // API Timeouts (em milissegundos)
  API: {
    QUICK: 10000,         // 10s - Testes de conexão, validações rápidas
    NORMAL: 60000,        // 1min - Operações normais
    UPLOAD: 120000,       // 2min - Upload de arquivos
    PROCESSING: 900000,   // 15min - Processamento complexo CrewAI
    DOWNLOAD: 60000,      // 1min - Download de arquivos
  },
  
  // WebSocket Timeouts
  WEBSOCKET: {
    HEARTBEAT: 30000,     // 30s - Intervalo de ping/pong
    RECONNECT_BASE: 3000, // 3s - Base para reconexão exponencial
    MAX_RECONNECT: 30000, // 30s - Máximo delay de reconexão
    RECEIVE_TIMEOUT: 60000, // 1min - Timeout para receber mensagens
  },
  
  // Retry Configurations
  RETRY: {
    MAX_ATTEMPTS: 3,      // Máximo de tentativas
    EXPONENTIAL_BASE: 2,  // Base para delay exponencial
    INITIAL_DELAY: 1000,  // 1s - Delay inicial
  }
}

export default TIMEOUTS