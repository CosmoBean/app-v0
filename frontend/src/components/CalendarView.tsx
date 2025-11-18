import { useState, useEffect } from 'react'
import { Calendar, Clock, MapPin, Users, Loader2 } from 'lucide-react'
import { calendarAPI } from '../services/api'
import { CalendarEvent } from '../types'
import { format, parseISO } from 'date-fns'

export default function CalendarView() {
  const [events, setEvents] = useState<CalendarEvent[]>([])
  const [loading, setLoading] = useState(true)
  const [view, setView] = useState<'today' | 'week'>('today')

  useEffect(() => {
    loadEvents()
  }, [view])

  const loadEvents = async () => {
    setLoading(true)
    try {
      const response =
        view === 'today'
          ? await calendarAPI.getTodayEvents()
          : await calendarAPI.getWeekEvents()

      setEvents(response.events || [])
    } catch (error) {
      console.error('Error loading events:', error)
    } finally {
      setLoading(false)
    }
  }

  const formatEventTime = (event: CalendarEvent) => {
    try {
      const start = parseISO(event.start.dateTime)
      const end = parseISO(event.end.dateTime)
      return `${format(start, 'h:mm a')} - ${format(end, 'h:mm a')}`
    } catch {
      return 'Time not available'
    }
  }

  const formatEventDate = (event: CalendarEvent) => {
    try {
      const start = parseISO(event.start.dateTime)
      return format(start, 'EEEE, MMMM d, yyyy')
    } catch {
      return 'Date not available'
    }
  }

  return (
    <div className="h-full flex flex-col bg-white dark:bg-gray-800 p-6">
      <div className="mb-6">
        <div className="flex items-center justify-between mb-4">
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
            Calendar
          </h1>
          <div className="flex gap-2">
            <button
              onClick={() => setView('today')}
              className={`px-4 py-2 rounded-lg text-sm font-medium ${
                view === 'today'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300'
              }`}
            >
              Today
            </button>
            <button
              onClick={() => setView('week')}
              className={`px-4 py-2 rounded-lg text-sm font-medium ${
                view === 'week'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300'
              }`}
            >
              This Week
            </button>
          </div>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto">
        {loading ? (
          <div className="flex items-center justify-center h-32">
            <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
          </div>
        ) : events.length === 0 ? (
          <div className="text-center py-12">
            <Calendar className="w-16 h-16 mx-auto mb-4 text-gray-400 dark:text-gray-600" />
            <p className="text-gray-500 dark:text-gray-400">
              No events scheduled for {view === 'today' ? 'today' : 'this week'}
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            {events.map((event) => (
              <div
                key={event.id}
                className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4 border-l-4 border-blue-600"
              >
                <div className="flex items-start justify-between mb-2">
                  <h3 className="font-semibold text-lg text-gray-900 dark:text-white">
                    {event.summary || 'Untitled Event'}
                  </h3>
                </div>

                <div className="space-y-2 text-sm text-gray-600 dark:text-gray-400">
                  <div className="flex items-center gap-2">
                    <Calendar className="w-4 h-4" />
                    <span>{formatEventDate(event)}</span>
                  </div>

                  <div className="flex items-center gap-2">
                    <Clock className="w-4 h-4" />
                    <span>{formatEventTime(event)}</span>
                  </div>

                  {event.location && (
                    <div className="flex items-center gap-2">
                      <MapPin className="w-4 h-4" />
                      <span>{event.location}</span>
                    </div>
                  )}

                  {event.attendees && event.attendees.length > 0 && (
                    <div className="flex items-center gap-2">
                      <Users className="w-4 h-4" />
                      <span>{event.attendees.length} attendees</span>
                    </div>
                  )}
                </div>

                {event.description && (
                  <p className="mt-3 text-sm text-gray-700 dark:text-gray-300">
                    {event.description}
                  </p>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
