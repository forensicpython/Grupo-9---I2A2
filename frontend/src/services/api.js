import axios from 'axios'
import { TIMEOUTS } from '../config/timeouts'

const API_BASE_URL = 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: TIMEOUTS.API.NORMAL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Configurações específicas para diferentes endpoints
const createApiWithTimeout = (timeout) => axios.create({
  baseURL: API_BASE_URL,
  timeout,
  headers: {
    'Content-Type': 'application/json',
  },
})

const quickApi = createApiWithTimeout(TIMEOUTS.API.QUICK)
const longApi = createApiWithTimeout(TIMEOUTS.API.PROCESSING)

// Request interceptor para adicionar token de auth
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor para tratamento de erros e retry
const createResponseInterceptor = (apiInstance) => {
  apiInstance.interceptors.response.use(
    (response) => response,
    async (error) => {
      const config = error.config
      
      // Se não foi definido, inicia contador de retry
      if (!config.__retryCount) {
        config.__retryCount = 0
      }
      
      // Retry para erros de rede ou timeout (max tentativas configuráveis)
      const shouldRetry = (
        config.__retryCount < TIMEOUTS.RETRY.MAX_ATTEMPTS &&
        (error.code === 'ECONNABORTED' || 
         error.code === 'NETWORK_ERROR' ||
         error.response?.status >= 500)
      )
      
      if (shouldRetry) {
        config.__retryCount += 1
        console.log(`Retry ${config.__retryCount}/${TIMEOUTS.RETRY.MAX_ATTEMPTS} for ${config.url}`)
        
        // Delay exponencial configurável
        const delay = Math.pow(TIMEOUTS.RETRY.EXPONENTIAL_BASE, config.__retryCount - 1) * TIMEOUTS.RETRY.INITIAL_DELAY
        await new Promise(resolve => setTimeout(resolve, delay))
        
        return apiInstance(config)
      }
      
      // Tratamento de autenticação
      if (error.response?.status === 401) {
        localStorage.removeItem('auth_token')
        window.location.href = '/'
      }
      
      return Promise.reject(error)
    }
  )
}

// Aplica interceptors em todas as instâncias
createResponseInterceptor(api)
createResponseInterceptor(quickApi)
createResponseInterceptor(longApi)

export const authAPI = {
  login: (credentials) => api.post('/auth/login', credentials),
  logout: () => api.post('/auth/logout'),
  refresh: () => api.post('/auth/refresh'),
}

export const filesAPI = {
  upload: (formData, onProgress) => {
    return longApi.post('/api/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: onProgress,
      timeout: TIMEOUTS.API.UPLOAD,
    })
  },
  process: (fileId, pergunta = 'Analise os dados das notas fiscais', apiKey, model) => {
    return longApi.post(`/api/process/${fileId}`, {
      apiKey: apiKey,
      model: model,
      pergunta: pergunta
    }, {
      timeout: TIMEOUTS.API.PROCESSING,
    })
  },
  download: (fileId) => api.get(`/api/files/${fileId}/download`, {
    responseType: 'blob',
    timeout: TIMEOUTS.API.DOWNLOAD,
  }),
}

export const groqAPI = {
  testConnection: (apiKey, model) => quickApi.post('/api/groq/test', { apiKey, model }, {
    timeout: TIMEOUTS.API.QUICK,
  }),
}

export const analysisAPI = {
  query: (question, context) => api.post('/analysis/query', { question, context }),
  getSuggestions: () => api.get('/analysis/suggestions'),
  getStats: () => api.get('/analysis/stats'),
  exportChat: (chatHistory) => api.post('/analysis/export', { chatHistory }, {
    responseType: 'blob',
  }),
}

export default api