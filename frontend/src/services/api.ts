import axios, { AxiosError, AxiosInstance } from 'axios'
import { useAuthStore } from '../store/authStore'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

// Create axios instance
const api: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor - add auth token
api.interceptors.request.use(
  (config) => {
    const { accessToken } = useAuthStore.getState()
    if (accessToken) {
      config.headers.Authorization = `Bearer ${accessToken}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// Response interceptor - handle errors
api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as any
    
    // Handle 401 Unauthorized
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true
      
      try {
        // Try to refresh token
        const { refreshToken } = useAuthStore.getState()
        if (refreshToken) {
          const response = await axios.post(`${API_BASE_URL}/api/v1/auth/refresh`, {
            refresh_token: refreshToken,
          })
          
          const { access_token, refresh_token } = response.data
          const { user } = useAuthStore.getState()
          
          if (user) {
            useAuthStore.getState().setAuth(user, access_token, refresh_token)
          }
          
          // Retry original request
          originalRequest.headers.Authorization = `Bearer ${access_token}`
          return api(originalRequest)
        }
      } catch (refreshError) {
        // Refresh failed, logout user
        useAuthStore.getState().clearAuth()
        window.location.href = '/login'
        return Promise.reject(refreshError)
      }
    }
    
    return Promise.reject(error)
  }
)

// API methods

export const authApi = {
  login: async (username: string, password: string) => {
    const response = await api.post('/api/v1/auth/login', { username, password })
    return response.data
  },
  
  register: async (email: string, username: string, password: string) => {
    const response = await api.post('/api/v1/auth/register', {
      email,
      username,
      password,
    })
    return response.data
  },
  
  getCurrentUser: async () => {
    const response = await api.get('/api/v1/auth/me')
    return response.data
  },
}

export const queryApi = {
  execute: async (question: string, database_id: number) => {
    const response = await api.post('/api/v1/query/execute', {
      question,
      database_id,
    })
    return response.data
  },
  
  getHistory: async (limit = 50, offset = 0) => {
    const response = await api.get('/api/v1/query/history', {
      params: { limit, offset },
    })
    return response.data
  },
  
  getQuery: async (queryId: number) => {
    const response = await api.get(`/api/v1/query/${queryId}`)
    return response.data
  },
}

export const databaseApi = {
  list: async () => {
    const response = await api.get('/api/v1/databases')
    return response.data
  },
  
  get: async (id: number) => {
    const response = await api.get(`/api/v1/databases/${id}`)
    return response.data
  },
  
  create: async (data: {
    name: string
    description?: string
    database_type: string
    connection_string: string
  }) => {
    const response = await api.post('/api/v1/databases', data)
    return response.data
  },
  
  update: async (
    id: number,
    data: {
      name: string
      description?: string
      database_type: string
      connection_string?: string
    }
  ) => {
    const response = await api.put(`/api/v1/databases/${id}`, data)
    return response.data
  },
  
  delete: async (id: number) => {
    const response = await api.delete(`/api/v1/databases/${id}`)
    return response.data
  },
  
  test: async (id: number) => {
    const response = await api.post(`/api/v1/databases/${id}/test`)
    return response.data
  },
  
  getSchema: async (id: number) => {
    const response = await api.get(`/api/v1/databases/${id}/schema`)
    return response.data
  },
  
  getTableSample: async (id: number, tableName: string, limit = 10) => {
    const response = await api.get(
      `/api/v1/databases/${id}/tables/${tableName}/sample`,
      { params: { limit } }
    )
    return response.data
  },
}

export const adminSetupApi = {
  chat: async (data: { message: string; context?: any }) => {
    const response = await api.post('/api/v1/admin/setup/chat', data)
    return response.data
  },
  
  selectDatabase: async (data: { database_type: string; context?: any }) => {
    const response = await api.post('/api/v1/admin/setup/select-database', data)
    return response.data
  },
  
  getDatabaseTypes: async () => {
    const response = await api.get('/api/v1/admin/setup/database-types')
    return response.data
  },
  
  resetConversation: async () => {
    const response = await api.post('/api/v1/admin/setup/reset-conversation')
    return response.data
  },
}

export default api

