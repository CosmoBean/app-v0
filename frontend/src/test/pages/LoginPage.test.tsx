import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent, waitFor } from '../utils/test-utils'
import LoginPage from '../../pages/LoginPage'
import * as api from '../../services/api'

vi.mock('../../services/api')

describe('LoginPage', () => {
  it('should render app name', () => {
    render(<LoginPage />)
    expect(screen.getByText('Gmail AI Organizer')).toBeInTheDocument()
  })

  it('should display sign in button', () => {
    render(<LoginPage />)
    expect(screen.getByRole('button', { name: /sign in with google/i })).toBeInTheDocument()
  })

  it('should display feature list', () => {
    render(<LoginPage />)
    expect(screen.getByText(/AI-powered email summarization/i)).toBeInTheDocument()
    expect(screen.getByText(/Calendar integration/i)).toBeInTheDocument()
    expect(screen.getByText(/Open source/i)).toBeInTheDocument()
  })

  it('should call login API when sign in button clicked', async () => {
    const loginSpy = vi.spyOn(api.authAPI, 'login').mockResolvedValue({
      authorization_url: 'https://accounts.google.com/o/oauth2/auth',
      state: 'test_state',
    })

    // Mock window.location.href
    delete (window as any).location
    window.location = { href: '' } as any

    render(<LoginPage />)

    const signInButton = screen.getByRole('button', { name: /sign in with google/i })
    fireEvent.click(signInButton)

    await waitFor(() => {
      expect(loginSpy).toHaveBeenCalled()
    })
  })

  it('should display feature icons', () => {
    render(<LoginPage />)
    // Check for feature section headings
    expect(screen.getByText('AI-Powered')).toBeInTheDocument()
    expect(screen.getByText('Calendar Integration')).toBeInTheDocument()
    expect(screen.getByText('Smart Organization')).toBeInTheDocument()
  })
})
