import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface User {
  id: number
  email: string
  username: string
  full_name?: string
  role: string  // 'admin', 'analyst', 'viewer'
  is_superuser: boolean
}

interface AuthState {
  user: User | null
  accessToken: string | null
  refreshToken: string | null
  isAuthenticated: boolean
  
  setAuth: (user: User, accessToken: string, refreshToken: string) => void
  clearAuth: () => void
  isAdmin: () => boolean
  isAnalyst: () => boolean
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      accessToken: null,
      refreshToken: null,
      isAuthenticated: false,
      
      setAuth: (user, accessToken, refreshToken) =>
        set({
          user,
          accessToken,
          refreshToken,
          isAuthenticated: true,
        }),
      
      clearAuth: () =>
        set({
          user: null,
          accessToken: null,
          refreshToken: null,
          isAuthenticated: false,
        }),
      
      isAdmin: () => {
        const { user } = get()
        return user?.is_superuser || user?.role === 'admin'
      },
      
      isAnalyst: () => {
        const { user } = get()
        return user?.role === 'analyst' || user?.role === 'admin' || user?.is_superuser
      },
    }),
    {
      name: 'auth-storage',
    }
  )
)

