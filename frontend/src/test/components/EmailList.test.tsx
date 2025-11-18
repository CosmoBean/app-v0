import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '../utils/test-utils'
import EmailList from '../../components/EmailList'
import * as api from '../../services/api'
import { mockEmails } from '../mocks/mockData'

vi.mock('../../services/api')

describe('EmailList', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('should render loading state initially', () => {
    vi.spyOn(api.gmailAPI, 'getMessages').mockImplementation(
      () => new Promise(() => {}) // Never resolves
    )

    render(<EmailList />)
    expect(screen.getByRole('status', { hidden: true })).toBeInTheDocument()
  })

  it('should display emails after loading', async () => {
    vi.spyOn(api.gmailAPI, 'getMessages').mockResolvedValue({
      messages: mockEmails,
      total: mockEmails.length,
    })

    render(<EmailList />)

    await waitFor(() => {
      expect(screen.getByText('Test Email 0')).toBeInTheDocument()
    })
  })

  it('should filter emails by unread', async () => {
    const getMessagesSpy = vi.spyOn(api.gmailAPI, 'getMessages').mockResolvedValue({
      messages: mockEmails,
      total: mockEmails.length,
    })

    render(<EmailList />)

    const unreadButton = screen.getByRole('button', { name: /unread/i })
    fireEvent.click(unreadButton)

    await waitFor(() => {
      expect(getMessagesSpy).toHaveBeenCalledWith(
        expect.objectContaining({ query: 'is:unread' })
      )
    })
  })

  it('should display selected email details', async () => {
    vi.spyOn(api.gmailAPI, 'getMessages').mockResolvedValue({
      messages: mockEmails,
      total: mockEmails.length,
    })

    render(<EmailList />)

    await waitFor(() => {
      const firstEmail = screen.getByText('Test Email 0')
      fireEvent.click(firstEmail)
    })

    await waitFor(() => {
      expect(screen.getByText('This is the full body of the test email.')).toBeInTheDocument()
    })
  })

  it('should archive email', async () => {
    vi.spyOn(api.gmailAPI, 'getMessages').mockResolvedValue({
      messages: mockEmails,
      total: mockEmails.length,
    })

    const archiveSpy = vi.spyOn(api.gmailAPI, 'archiveMessage').mockResolvedValue({
      status: 'archived',
      message_id: 'email0',
    })

    render(<EmailList />)

    await waitFor(() => {
      const firstEmail = screen.getByText('Test Email 0')
      fireEvent.click(firstEmail)
    })

    const archiveButton = screen.getByTitle('Archive')
    fireEvent.click(archiveButton)

    await waitFor(() => {
      expect(archiveSpy).toHaveBeenCalledWith('email0')
    })
  })

  it('should show empty state when no emails', async () => {
    vi.spyOn(api.gmailAPI, 'getMessages').mockResolvedValue({
      messages: [],
      total: 0,
    })

    render(<EmailList />)

    await waitFor(() => {
      expect(screen.getByText(/No emails found/i)).toBeInTheDocument()
    })
  })
})
