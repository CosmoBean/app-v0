import { Email, CalendarEvent, ChatMessage } from '../../types'

export const mockEmail: Email = {
  id: 'email123',
  thread_id: 'thread123',
  subject: 'Test Email Subject',
  from: 'sender@example.com',
  to: 'recipient@example.com',
  snippet: 'This is a test email snippet',
  body_text: 'This is the full body of the test email.',
  date: 'Mon, 1 Jan 2024 10:00:00 -0800',
  labels: ['INBOX', 'UNREAD'],
  summary: 'AI generated summary',
  category: 'work',
  ai_tags: ['meeting', 'project'],
  priority_score: 75,
}

export const mockCalendarEvent: CalendarEvent = {
  id: 'event123',
  summary: 'Team Meeting',
  description: 'Weekly team sync',
  start: {
    dateTime: '2024-01-15T14:00:00-08:00',
    timeZone: 'America/Los_Angeles',
  },
  end: {
    dateTime: '2024-01-15T15:00:00-08:00',
    timeZone: 'America/Los_Angeles',
  },
  location: 'Conference Room A',
  attendees: [{ email: 'colleague@example.com' }],
}

export const mockChatMessage: ChatMessage = {
  role: 'user',
  content: 'Summarize my unread emails',
  timestamp: '2024-01-01T10:00:00Z',
}

export const mockEmails = Array.from({ length: 10 }, (_, i) => ({
  ...mockEmail,
  id: `email${i}`,
  subject: `Test Email ${i}`,
}))

export const mockCalendarEvents = Array.from({ length: 5 }, (_, i) => ({
  ...mockCalendarEvent,
  id: `event${i}`,
  summary: `Meeting ${i}`,
}))
