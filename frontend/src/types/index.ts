export interface Email {
  id: string
  thread_id: string
  subject: string
  from: string
  to: string
  snippet: string
  body_text: string
  date: string
  labels: string[]
  summary?: string
  category?: string
  ai_tags?: string[]
  priority_score?: number
}

export interface CalendarEvent {
  id: string
  summary: string
  description?: string
  start: {
    dateTime: string
    timeZone?: string
  }
  end: {
    dateTime: string
    timeZone?: string
  }
  location?: string
  attendees?: Array<{
    email: string
  }>
}

export interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
  timestamp?: string
}

export interface ChatResponse {
  message: string
  actions_taken?: Array<{
    action: string
    [key: string]: any
  }>
  context_used?: {
    emails?: any
    calendar?: any
  }
}

export interface QuickAction {
  id: string
  label: string
  icon: string
  action: string
  description: string
}
