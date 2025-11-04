import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from './store/authStore'
import Layout from './components/Layout'
import LoginPage from './pages/LoginPage'
import SimpleChatPage from './pages/SimpleChatPage'
import AdminDashboard from './pages/AdminDashboard'

function App() {
  const { isAuthenticated, user } = useAuthStore()

  // Determine default route based on user role
  const getDefaultRoute = () => {
    if (user?.role === 'admin') {
      return <AdminDashboard />
    }
    return <SimpleChatPage />
  }

  return (
    <Router>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        
        {/* Protected routes */}
        <Route
          path="/"
          element={isAuthenticated ? <Layout /> : <Navigate to="/login" />}
        >
          <Route index element={getDefaultRoute()} />
          <Route path="chat" element={<SimpleChatPage />} />
          <Route path="admin" element={<AdminDashboard />} />
        </Route>
      </Routes>
    </Router>
  )
}

export default App

