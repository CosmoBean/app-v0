import axios from 'axios'
import { useAuthStore } from '../store/authStore'
import { Email, CalendarEvent, ChatMessage, ChatResponse } from '../types'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
})

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = useAuthStore.getState().accessToken
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Auth APIs
export const authAPI = {
  login: async () => {
    const response = await api.get('/auth/login')
    return response.data
  },
  callback: async (code: string) => {
    const response = await api.post('/auth/callback', { code })
    return response.data
  },
  logout: async () => {
    const response = await api.post('/auth/logout')
    return response.data
  },
}

// Gmail APIs
export const gmailAPI = {
  getMessages: async (params: {
    max_results?: number
    query?: string
    label_ids?: string[]
  }) => {
    const response = await api.post<{ messages: Email[]; total: number }>(
      '/gmail/messages',
      params
    )
    return response.data
  },

  getMessage: async (messageId: string) => {
    const response = await api.get<Email>(`/gmail/messages/${messageId}`)
    return response.data
  },

  summarizeEmail: async (messageId: string) => {
    const response = await api.post(`/gmail/messages/${messageId}/summarize`)
    return response.data
  },

  archiveMessage: async (messageId: string) => {
    const response = await api.post(`/gmail/messages/${messageId}/archive`)
    return response.data
  },

  trashMessage: async (messageId: string) => {
    const response = await api.post(`/gmail/messages/${messageId}/trash`)
    return response.data
  },

  processBatch: async (params: {
    message_ids?: string[]
    query?: string
    max_results?: number
    auto_categorize?: boolean
    apply_labels?: boolean
  }) => {
    const response = await api.post('/gmail/process-batch', params)
    return response.data
  },

  getLabels: async () => {
    const response = await api.get('/gmail/labels')
    return response.data
  },
}

// Calendar APIs
export const calendarAPI = {
  getEvents: async (params: {
    time_min?: string
    time_max?: string
    max_results?: number
  }) => {
    const response = await api.post<{ events: CalendarEvent[]; total: number }>(
      '/calendar/events',
      params
    )
    return response.data
  },

  getTodayEvents: async () => {
    const response = await api.get<{ events: CalendarEvent[] }>(
      '/calendar/events/today'
    )
    return response.data
  },

  getWeekEvents: async () => {
    const response = await api.get<{ events: CalendarEvent[] }>(
      '/calendar/events/week'
    )
    return response.data
  },

  createEvent: async (event: {
    summary: string
    start_time: string
    end_time: string
    description?: string
    location?: string
    attendees?: string[]
  }) => {
    const response = await api.post('/calendar/events/create', event)
    return response.data
  },

  quickAdd: async (text: string) => {
    const response = await api.post('/calendar/events/quick-add', { text })
    return response.data
  },
}

// Chat APIs
export const chatAPI = {
  sendMessage: async (
    messages: ChatMessage[],
    options?: {
      include_email_context?: boolean
      include_calendar_context?: boolean
      max_context_items?: number
    }
  ) => {
    const response = await api.post<ChatResponse>('/chat/message', {
      messages,
      include_email_context: options?.include_email_context ?? true,
      include_calendar_context: options?.include_calendar_context ?? true,
      max_context_items: options?.max_context_items ?? 10,
    })
    return response.data
  },

  quickAction: async (action: string, parameters?: any) => {
    const response = await api.post('/chat/quick-action', {
      action,
      parameters,
    })
    return response.data
  },

  getSuggestions: async () => {
    const response = await api.get('/chat/suggestions')
    return response.data
  },
}
