import { Outlet, Link, useNavigate, useLocation } from 'react-router-dom'
import { useAuthStore } from '../store/authStore'
import { Database, LogOut, User, Shield, MessageSquare, Settings } from 'lucide-react'

export default function Layout() {
  const { user, clearAuth, isAdmin } = useAuthStore()
  const navigate = useNavigate()
  const location = useLocation()

  const handleLogout = () => {
    clearAuth()
    navigate('/login')
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border bg-card">
        <div className="container mx-auto px-4">
          <div className="flex h-16 items-center justify-between">
            {/* Logo */}
            <Link to="/" className="flex items-center space-x-2">
              <Database className="h-6 w-6 text-primary" />
              <span className="text-xl font-bold">AgentMedha</span>
            </Link>

            {/* Navigation - Role-Aware */}
            <nav className="flex items-center space-x-6">
              {isAdmin() ? (
                // Admin Navigation
                <Link
                  to="/admin"
                  className={`flex items-center gap-1.5 text-sm font-medium transition-colors ${
                    location.pathname === '/admin' || location.pathname === '/'
                      ? 'text-primary'
                      : 'hover:text-primary'
                  }`}
                >
                  <Settings className="h-4 w-4" />
                  Admin Dashboard
                </Link>
              ) : (
                // Regular User Navigation
                <Link
                  to="/chat"
                  className={`flex items-center gap-1.5 text-sm font-medium transition-colors ${
                    location.pathname === '/chat' || location.pathname === '/'
                      ? 'text-primary'
                      : 'hover:text-primary'
                  }`}
                >
                  <MessageSquare className="h-4 w-4" />
                  Chat
                </Link>
              )}
            </nav>

            {/* User menu */}
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <User className="h-4 w-4 text-muted-foreground" />
                <span className="text-sm text-muted-foreground">
                  {user?.username || 'User'}
                </span>
                {isAdmin() && (
                  <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium bg-primary/10 text-primary">
                    <Shield className="h-3 w-3" />
                    Admin
                  </span>
                )}
              </div>
              <button
                onClick={handleLogout}
                className="flex items-center space-x-2 text-sm text-muted-foreground hover:text-primary transition-colors"
              >
                <LogOut className="h-4 w-4" />
                <span>Logout</span>
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main content */}
      <main className="container mx-auto px-4 py-8">
        <Outlet />
      </main>
    </div>
  )
}

