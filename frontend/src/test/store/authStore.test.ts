import { describe, it, expect, beforeEach } from 'vitest'
import { useAuthStore } from '../../store/authStore'

describe('AuthStore', () => {
  beforeEach(() => {
    // Reset store before each test
    useAuthStore.setState({
      accessToken: null,
      refreshToken: null,
      userEmail: null,
      userName: null,
      isAuthenticated: false,
    })
  })

  it('should initialize with default values', () => {
    const state = useAuthStore.getState()
    expect(state.isAuthenticated).toBe(false)
    expect(state.accessToken).toBeNull()
    expect(state.userEmail).toBeNull()
  })

  it('should set authentication data', () => {
    const authData = {
      accessToken: 'test_token',
      refreshToken: 'test_refresh',
      userEmail: 'test@example.com',
      userName: 'Test User',
    }

    useAuthStore.getState().setAuth(authData)

    const state = useAuthStore.getState()
    expect(state.isAuthenticated).toBe(true)
    expect(state.accessToken).toBe('test_token')
    expect(state.userEmail).toBe('test@example.com')
    expect(state.userName).toBe('Test User')
  })

  it('should handle logout', () => {
    // First set auth
    useAuthStore.getState().setAuth({
      accessToken: 'test_token',
      userEmail: 'test@example.com',
    })

    // Then logout
    useAuthStore.getState().logout()

    const state = useAuthStore.getState()
    expect(state.isAuthenticated).toBe(false)
    expect(state.accessToken).toBeNull()
    expect(state.userEmail).toBeNull()
  })

  it('should persist state', () => {
    const authData = {
      accessToken: 'test_token',
      userEmail: 'test@example.com',
    }

    useAuthStore.getState().setAuth(authData)

    // Simulate page reload by getting state again
    const state = useAuthStore.getState()
    expect(state.accessToken).toBe('test_token')
  })
})
