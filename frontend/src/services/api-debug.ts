// Debug version to see what's happening
import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

console.log('🔍 API Base URL:', API_BASE_URL)

export const testLogin = async () => {
  console.log('🧪 Testing login...')
  try {
    const response = await axios.post(`${API_BASE_URL}/api/v1/auth/login`, {
      username: 'admin',
      password: 'admin123'
    }, {
      headers: {
        'Content-Type': 'application/json'
      }
    })
    console.log('✅ Login successful!', response.data)
    return response.data
  } catch (error: any) {
    console.error('❌ Login failed:', {
      message: error.message,
      response: error.response?.data,
      status: error.response?.status,
      headers: error.response?.headers
    })
    throw error
  }
}

// Auto-test on load
testLogin().then(() => {
  console.log('✅ Auto-test passed!')
}).catch(() => {
  console.log('❌ Auto-test failed!')
})
