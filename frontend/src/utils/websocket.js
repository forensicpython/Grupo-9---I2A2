import { TIMEOUTS } from '../config/timeouts'

class WebSocketManager {
  constructor() {
    this.ws = null
    this.reconnectAttempts = 0
    this.maxReconnectAttempts = 10
    this.reconnectInterval = TIMEOUTS.WEBSOCKET.RECONNECT_BASE
    this.listeners = new Map()
    this.isConnecting = false
    this.heartbeatInterval = null
    this.connectionUrl = null
  }

  connect(url = 'ws://localhost:8000/ws') {
    if (this.isConnecting) {
      console.log('WebSocket já está tentando conectar...')
      return
    }

    this.connectionUrl = url
    this.isConnecting = true
    
    try {
      this.ws = new WebSocket(url)
      
      this.ws.onopen = () => {
        console.log('WebSocket connected')
        this.isConnecting = false
        this.reconnectAttempts = 0
        this.notifyListeners('connected', true)
        this.startHeartbeat()
      }

      this.ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          
          // Ignora mensagens de pong do heartbeat
          if (data.type === 'pong') {
            return
          }
          
          this.notifyListeners('message', data)
          
          // Handle specific message types
          if (data.type) {
            this.notifyListeners(data.type, data)
          }
        } catch (error) {
          console.error('Error parsing WebSocket message:', error)
        }
      }

      this.ws.onclose = (event) => {
        console.log('WebSocket disconnected:', event.code, event.reason)
        this.isConnecting = false
        this.stopHeartbeat()
        this.notifyListeners('connected', false)
        
        // Só reconecta se não foi um fechamento intencional
        if (event.code !== 1000) {
          this.attemptReconnect()
        }
      }

      this.ws.onerror = (error) => {
        console.error('WebSocket error:', error)
        this.isConnecting = false
        this.notifyListeners('error', error)
      }
    } catch (error) {
      console.error('Error connecting to WebSocket:', error)
      this.isConnecting = false
    }
  }

  disconnect() {
    this.stopHeartbeat()
    if (this.ws) {
      this.ws.close(1000, 'Cliente desconectando')
      this.ws = null
    }
  }

  startHeartbeat() {
    this.stopHeartbeat()
    this.heartbeatInterval = setInterval(() => {
      if (this.ws && this.ws.readyState === WebSocket.OPEN) {
        this.ws.send(JSON.stringify({ type: 'ping', timestamp: Date.now() }))
      }
    }, TIMEOUTS.WEBSOCKET.HEARTBEAT)
  }

  stopHeartbeat() {
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval)
      this.heartbeatInterval = null
    }
  }

  send(data) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data))
    } else {
      console.warn('WebSocket is not connected')
    }
  }

  attemptReconnect() {
    if (this.isConnecting) {
      return
    }

    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++
      const delay = Math.min(
        this.reconnectInterval * Math.pow(2, this.reconnectAttempts - 1), 
        TIMEOUTS.WEBSOCKET.MAX_RECONNECT
      )
      
      console.log(`Attempting to reconnect... (${this.reconnectAttempts}/${this.maxReconnectAttempts}) in ${delay}ms`)
      
      setTimeout(() => {
        if (this.connectionUrl) {
          this.connect(this.connectionUrl)
        }
      }, delay)
    } else {
      console.log('Max reconnection attempts reached')
      this.notifyListeners('max_reconnect_reached', true)
    }
  }

  on(event, callback) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, [])
    }
    this.listeners.get(event).push(callback)
  }

  off(event, callback) {
    if (this.listeners.has(event)) {
      const callbacks = this.listeners.get(event)
      const index = callbacks.indexOf(callback)
      if (index > -1) {
        callbacks.splice(index, 1)
      }
    }
  }

  notifyListeners(event, data) {
    if (this.listeners.has(event)) {
      this.listeners.get(event).forEach(callback => {
        try {
          callback(data)
        } catch (error) {
          console.error('Error in WebSocket listener:', error)
        }
      })
    }
  }
}

export const wsManager = new WebSocketManager()
export default wsManager