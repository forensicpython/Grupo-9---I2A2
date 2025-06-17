import { useState } from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import LoginPage from './pages/LoginPage'
import Dashboard from './pages/Dashboard'
import AnalysisPage from './pages/AnalysisPage'

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [user, setUser] = useState(null)

  return (
    <Router>
      <div className="min-h-screen gradient-bg">
        <Routes>
          <Route 
            path="/" 
            element={
              <LoginPage 
                setIsAuthenticated={setIsAuthenticated}
                setUser={setUser}
              />
            } 
          />
          <Route 
            path="/dashboard" 
            element={<Dashboard user={user} />} 
          />
          <Route 
            path="/analyze" 
            element={<AnalysisPage user={user} />} 
          />
        </Routes>
      </div>
    </Router>
  )
}

export default App
