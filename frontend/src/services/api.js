import axios from 'axios'

// Base API URL
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor
api.interceptors.request.use(
  (config) => {
    // Add any auth headers here in the future
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
