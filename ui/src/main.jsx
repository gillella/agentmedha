import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.jsx'
import PWAUpdatePrompt from './components/PWAUpdatePrompt.jsx'
// PWAInstallPrompt removed - Chrome handles install natively

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <App />
    <PWAUpdatePrompt />
  </StrictMode>,
)
