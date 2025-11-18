import { useEffect } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { Mail, Sparkles, Calendar, Tags } from 'lucide-react'
import { useAuthStore } from '../store/authStore'
import { authAPI } from '../services/api'

export default function LoginPage() {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const setAuth = useAuthStore((state) => state.setAuth)
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated)

  useEffect(() => {
    if (isAuthenticated) {
      navigate('/dashboard')
    }
  }, [isAuthenticated, navigate])

  useEffect(() => {
    const code = searchParams.get('code')
    if (code) {
      handleCallback(code)
    }
  }, [searchParams])

  const handleCallback = async (code: string) => {
    try {
      const data = await authAPI.callback(code)
      setAuth({
        accessToken: data.access_token,
        refreshToken: data.refresh_token,
        userEmail: data.user_email,
        userName: data.user_name,
      })
      navigate('/dashboard')
    } catch (error) {
      console.error('Login failed:', error)
      alert('Login failed. Please try again.')
    }
  }

  const handleLogin = async () => {
    try {
      const data = await authAPI.login()
      window.location.href = data.authorization_url
    } catch (error) {
      console.error('Error initiating login:', error)
      alert('Failed to start login process')
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800 flex items-center justify-center p-4">
      <div className="max-w-4xl w-full">
        <div className="text-center mb-8">
          <div className="flex justify-center mb-4">
            <div className="bg-blue-600 p-4 rounded-2xl shadow-lg">
              <Mail className="w-12 h-12 text-white" />
            </div>
          </div>
          <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-2">
            Gmail AI Organizer
          </h1>
          <p className="text-lg text-gray-600 dark:text-gray-300">
            AI-powered email and calendar management
          </p>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-8 mb-8">
          <div className="grid md:grid-cols-3 gap-6 mb-8">
            <div className="text-center">
              <div className="bg-blue-100 dark:bg-blue-900 p-3 rounded-full w-16 h-16 mx-auto mb-3 flex items-center justify-center">
                <Sparkles className="w-8 h-8 text-blue-600 dark:text-blue-300" />
              </div>
              <h3 className="font-semibold text-gray-900 dark:text-white mb-1">
                AI-Powered
              </h3>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Automatic categorization and smart summaries
              </p>
            </div>

            <div className="text-center">
              <div className="bg-green-100 dark:bg-green-900 p-3 rounded-full w-16 h-16 mx-auto mb-3 flex items-center justify-center">
                <Calendar className="w-8 h-8 text-green-600 dark:text-green-300" />
              </div>
              <h3 className="font-semibold text-gray-900 dark:text-white mb-1">
                Calendar Integration
              </h3>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Manage schedule alongside emails
              </p>
            </div>

            <div className="text-center">
              <div className="bg-purple-100 dark:bg-purple-900 p-3 rounded-full w-16 h-16 mx-auto mb-3 flex items-center justify-center">
                <Tags className="w-8 h-8 text-purple-600 dark:text-purple-300" />
              </div>
              <h3 className="font-semibold text-gray-900 dark:text-white mb-1">
                Smart Organization
              </h3>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Auto-tag and filter important emails
              </p>
            </div>
          </div>

          <div className="text-center">
            <button
              onClick={handleLogin}
              className="bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-8 rounded-lg transition-colors duration-200 shadow-lg hover:shadow-xl"
            >
              Sign in with Google
            </button>
            <p className="text-xs text-gray-500 dark:text-gray-400 mt-4">
              Secure OAuth2 authentication • No password storage
            </p>
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-6">
          <h3 className="font-semibold text-gray-900 dark:text-white mb-4">
            Features
          </h3>
          <ul className="space-y-2 text-sm text-gray-600 dark:text-gray-400">
            <li className="flex items-center">
              <span className="text-green-500 mr-2">✓</span>
              AI-powered email summarization and categorization
            </li>
            <li className="flex items-center">
              <span className="text-green-500 mr-2">✓</span>
              Conversational interface for managing inbox
            </li>
            <li className="flex items-center">
              <span className="text-green-500 mr-2">✓</span>
              Calendar integration with smart scheduling
            </li>
            <li className="flex items-center">
              <span className="text-green-500 mr-2">✓</span>
              Free tier with project keys or BYOK (Bring Your Own Keys)
            </li>
            <li className="flex items-center">
              <span className="text-green-500 mr-2">✓</span>
              Open source and privacy-focused
            </li>
          </ul>
        </div>

        <p className="text-center text-sm text-gray-500 dark:text-gray-400 mt-6">
          Open Source • Privacy First • Built with ❤️
        </p>
      </div>
    </div>
  )
}
