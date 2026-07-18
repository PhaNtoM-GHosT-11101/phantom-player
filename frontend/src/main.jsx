import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import { PlayerProvider } from './context/PlayerContext'
import { AuthProvider } from './context/AuthContext'
import App from './App.jsx'
import './index.css'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <BrowserRouter>
      <AuthProvider>
        <PlayerProvider>
          <App />
        </PlayerProvider>
      </AuthProvider>
    </BrowserRouter>
  </StrictMode>,
)
