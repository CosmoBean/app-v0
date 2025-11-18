import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent, waitFor } from '../utils/test-utils'
import CalendarView from '../../components/CalendarView'
import * as api from '../../services/api'
import { mockCalendarEvents } from '../mocks/mockData'

vi.mock('../../services/api')

describe('CalendarView', () => {
  it('should render calendar header', () => {
    render(<CalendarView />)
    expect(screen.getByText('Calendar')).toBeInTheDocument()
  })

  it('should display today button', () => {
    render(<CalendarView />)
    expect(screen.getByRole('button', { name: /today/i })).toBeInTheDocument()
  })

  it('should display week button', () => {
    render(<CalendarView />)
    expect(screen.getByRole('button', { name: /this week/i })).toBeInTheDocument()
  })

  it('should load and display events', async () => {
    vi.spyOn(api.calendarAPI, 'getTodayEvents').mockResolvedValue({
      events: mockCalendarEvents,
    })

    render(<CalendarView />)

    await waitFor(() => {
      expect(screen.getByText('Meeting 0')).toBeInTheDocument()
    })
  })

  it('should switch between today and week view', async () => {
    const getTodaySpy = vi.spyOn(api.calendarAPI, 'getTodayEvents').mockResolvedValue({
      events: mockCalendarEvents,
    })

    const getWeekSpy = vi.spyOn(api.calendarAPI, 'getWeekEvents').mockResolvedValue({
      events: mockCalendarEvents,
    })

    render(<CalendarView />)

    await waitFor(() => {
      expect(getTodaySpy).toHaveBeenCalled()
    })

    const weekButton = screen.getByRole('button', { name: /this week/i })
    fireEvent.click(weekButton)

    await waitFor(() => {
      expect(getWeekSpy).toHaveBeenCalled()
    })
  })

  it('should show empty state when no events', async () => {
    vi.spyOn(api.calendarAPI, 'getTodayEvents').mockResolvedValue({
      events: [],
    })

    render(<CalendarView />)

    await waitFor(() => {
      expect(screen.getByText(/No events scheduled/i)).toBeInTheDocument()
    })
  })

  it('should display event details', async () => {
    vi.spyOn(api.calendarAPI, 'getTodayEvents').mockResolvedValue({
      events: mockCalendarEvents,
    })

    render(<CalendarView />)

    await waitFor(() => {
      expect(screen.getByText('Meeting 0')).toBeInTheDocument()
      expect(screen.getByText('Conference Room A')).toBeInTheDocument()
    })
  })
})
