import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent, waitFor } from '../utils/test-utils'
import ChatInterface from '../../components/ChatInterface'
import * as api from '../../services/api'

vi.mock('../../services/api')

describe('ChatInterface', () => {
  it('should render initial assistant message', () => {
    render(<ChatInterface />)
    expect(screen.getByText(/Hello! I'm your AI email assistant/i)).toBeInTheDocument()
  })

  it('should display quick action buttons initially', () => {
    render(<ChatInterface />)
    expect(screen.getByText(/Summarize unread emails/i)).toBeInTheDocument()
    expect(screen.getByText(/Show today's schedule/i)).toBeInTheDocument()
  })

  it('should allow user to type message', () => {
    render(<ChatInterface />)
    const input = screen.getByPlaceholderText(/Ask me anything/i) as HTMLTextAreaElement

    fireEvent.change(input, { target: { value: 'Test message' } })
    expect(input.value).toBe('Test message')
  })

  it('should send message on button click', async () => {
    vi.spyOn(api.chatAPI, 'sendMessage').mockResolvedValue({
      message: 'Test response',
      actions_taken: [],
    })

    render(<ChatInterface />)
    const input = screen.getByPlaceholderText(/Ask me anything/i)
    const sendButton = screen.getByRole('button', { name: /send/i })

    fireEvent.change(input, { target: { value: 'Test message' } })
    fireEvent.click(sendButton)

    await waitFor(() => {
      expect(screen.getByText('Test message')).toBeInTheDocument()
    })
  })

  it('should disable send button when input is empty', () => {
    render(<ChatInterface />)
    const sendButton = screen.getByRole('button', { name: /send/i })
    expect(sendButton).toBeDisabled()
  })

  it('should show loading state while sending message', async () => {
    vi.spyOn(api.chatAPI, 'sendMessage').mockImplementation(
      () => new Promise((resolve) => setTimeout(() => resolve({ message: 'Response', actions_taken: [] }), 100))
    )

    render(<ChatInterface />)
    const input = screen.getByPlaceholderText(/Ask me anything/i)
    const sendButton = screen.getByRole('button', { name: /send/i })

    fireEvent.change(input, { target: { value: 'Test' } })
    fireEvent.click(sendButton)

    // Check for loading indicator
    expect(sendButton).toBeDisabled()
  })
})
