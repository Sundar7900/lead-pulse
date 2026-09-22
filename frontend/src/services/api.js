import axios from 'axios'

// Dynamic Base API URL with localStorage override support
export const getApiBaseUrl = () => {
  const custom = typeof window !== 'undefined' ? localStorage.getItem('leadpulse_api_url') : null
  if (custom && custom.trim()) {
    return custom.trim().replace(/\/+$/, '')
  }
  
  const envUrl = import.meta.env.VITE_API_URL
  if (envUrl && envUrl.trim()) {
    return envUrl.trim().replace(/\/+$/, '')
  }

  return 'http://localhost:8000'
}

// Create axios instance
const api = axios.create({
  baseURL: getApiBaseUrl(),
  headers: {
    'Content-Type': 'application/json',
  },
})

// Update baseURL dynamically before every request
api.interceptors.request.use(
  (config) => {
    config.baseURL = getApiBaseUrl()
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor
api.interceptors.response.use(
  (response) => {
    return response.data
  },
  (error) => {
    // Handle errors
    const message = error.response?.data?.message || 'An error occurred'
    console.error('API Error:', message)
    return Promise.reject(error)
  }
)

// API helper functions
export const apiService = {
  // Generic request methods
  get: (url, params) => api.get(url, { params }),
  post: (url, data) => api.post(url, data),
  put: (url, data) => api.put(url, data),
  delete: (url) => api.delete(url),

  // Dashboard
  getDashboardSummary: () => api.get('/api/dashboard/summary'),
  getDashboardStatistics: () => api.get('/api/dashboard/statistics'),

  // Leads
  getLeads: (params) => api.get('/api/leads', { params }),
  getLead: (id) => api.get(`/api/leads/${id}`),
  createLead: (data) => api.post('/api/leads', data),
  updateLead: (id, data) => api.put(`/api/leads/${id}`, data),
  deleteLead: (id) => api.delete(`/api/leads/${id}`),
  getHighValueLeads: () => api.get('/api/leads/high-value'),
  calculateLeadScore: (id) => api.post(`/api/leads/${id}/calculate-score`),

  // Lead Activities
  getLeadActivities: (leadId) => api.get(`/api/leads/${leadId}/activities`),
  addLeadActivity: (leadId, data) => api.post(`/api/leads/${leadId}/activities`, data),

  // Alerts
  getAlerts: (params) => api.get('/api/alerts', { params }),
  markAlertAsRead: (id) => api.put(`/api/alerts/${id}/read`),

  // Health check
  healthCheck: () => api.get('/health'),
  getStatus: () => api.get('/api/status'),
}

export default api
