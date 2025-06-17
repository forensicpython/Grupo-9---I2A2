import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Eye, EyeOff, User, Lock, ArrowLeft } from 'lucide-react'
import instaprice from '../assets/Instaprice_2.png'

const LoginPage = ({ setIsAuthenticated, setUser }) => {
  const [showPassword, setShowPassword] = useState(false)
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [showDemo, setShowDemo] = useState(false)
  const navigate = useNavigate()

  const handleLogin = (e) => {
    e.preventDefault()
    
    let userType = null
    if ((username === 'admin' && password === 'admin123') || 
        (username === 'analista' && password === 'analista123')) {
      userType = username === 'admin' ? 'admin' : 'analista'
      setUser({ username, type: userType })
      setIsAuthenticated(true)
      navigate('/dashboard')
    } else {
      alert('Credenciais inválidas')
    }
  }

  const handleDemoUser = (type) => {
    if (type === 'admin') {
      setUsername('admin')
      setPassword('admin123')
    } else {
      setUsername('analista')
      setPassword('analista123')
    }
    setShowDemo(false)
  }

  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      {/* Background Pattern */}
      <div className="absolute inset-0 opacity-10">
        <div className="absolute inset-0 bg-gradient-to-br from-instaprice-primary/20 to-transparent"></div>
      </div>

      {/* Main Content */}
      <div className="relative w-full max-w-md">
        {/* Logo Section */}
        <div className="text-center mb-8">
          <img 
            src={instaprice} 
            alt="Instaprice" 
            className="h-40 mx-auto mb-6 drop-shadow-2xl"
          />
          <h1 className="text-2xl font-bold text-white mb-2">Login</h1>
        </div>

        {/* Login Form */}
        <div className="glass-effect rounded-2xl p-8 shadow-2xl">
          <form onSubmit={handleLogin} className="space-y-6">
            {/* Username Field */}
            <div className="space-y-2">
              <label className="flex items-center text-sm font-medium text-gray-300">
                <User className="w-4 h-4 mr-2" />
                Usuário
              </label>
              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="Digite seu usuário"
                className="w-full px-4 py-3 bg-gray-800/50 border border-gray-600 rounded-lg 
                         text-white placeholder-gray-400 focus:outline-none focus:ring-2 
                         focus:ring-instaprice-primary focus:border-transparent transition-all"
                required
              />
            </div>

            {/* Password Field */}
            <div className="space-y-2">
              <label className="flex items-center text-sm font-medium text-gray-300">
                <Lock className="w-4 h-4 mr-2" />
                Senha
              </label>
              <div className="relative">
                <input
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••••••••••••••••••"
                  className="w-full px-4 py-3 bg-gray-800/50 border border-gray-600 rounded-lg 
                           text-white placeholder-gray-400 focus:outline-none focus:ring-2 
                           focus:ring-instaprice-primary focus:border-transparent transition-all pr-12"
                  required
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 
                           hover:text-white transition-colors"
                >
                  {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                </button>
              </div>
            </div>

            {/* Login Button */}
            <button
              type="submit"
              className="w-full bg-gradient-to-r from-instaprice-primary to-instaprice-secondary 
                       text-white py-3 px-4 rounded-lg font-medium hover:shadow-lg 
                       hover:shadow-instaprice-primary/25 transition-all duration-300 
                       transform hover:scale-105"
            >
              ↗ Entrar
            </button>
          </form>

          {/* Demo Accounts */}
          <div className="mt-6 pt-6 border-t border-gray-600">
            <div className="text-center mb-4">
              <button
                onClick={() => setShowDemo(!showDemo)}
                className="flex items-center justify-center w-full text-sm text-instaprice-primary 
                         hover:text-white transition-colors"
              >
                ℹ Contas de Demonstração
              </button>
            </div>

            {showDemo && (
              <div className="space-y-3 animate-in slide-in-from-top duration-200">
                <button
                  onClick={() => handleDemoUser('admin')}
                  className="w-full flex items-center justify-between p-3 bg-blue-600/20 
                           border border-blue-500/30 rounded-lg hover:bg-blue-600/30 
                           transition-colors group"
                >
                  <div className="flex items-center">
                    <div className="w-2 h-2 bg-blue-400 rounded-full mr-3"></div>
                    <span className="text-white font-medium">Admin</span>
                  </div>
                  <div className="text-xs text-gray-400">
                    admin / admin123
                  </div>
                  <span className="text-blue-400 opacity-0 group-hover:opacity-100 transition-opacity">
                    Usar
                  </span>
                </button>

                <button
                  onClick={() => handleDemoUser('analista')}
                  className="w-full flex items-center justify-between p-3 bg-green-600/20 
                           border border-green-500/30 rounded-lg hover:bg-green-600/30 
                           transition-colors group"
                >
                  <div className="flex items-center">
                    <div className="w-2 h-2 bg-green-400 rounded-full mr-3"></div>
                    <span className="text-white font-medium">Analista</span>
                  </div>
                  <div className="text-xs text-gray-400">
                    analista / analista123
                  </div>
                  <span className="text-green-400 opacity-0 group-hover:opacity-100 transition-opacity">
                    Usar
                  </span>
                </button>
              </div>
            )}
          </div>

          {/* Back to Home */}
          <div className="mt-6 text-center">
            <button className="flex items-center text-sm text-gray-400 hover:text-white 
                             transition-colors mx-auto">
              <ArrowLeft className="w-4 h-4 mr-2" />
              Voltar ao início
            </button>
          </div>
        </div>

        {/* Security Notice */}
        <div className="mt-6 text-center text-xs text-gray-500">
          🔒 Conexão segura e criptografada
        </div>
      </div>
    </div>
  )
}

export default LoginPage