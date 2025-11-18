import { MessageSquare, Mail, Calendar, Settings, LogOut } from 'lucide-react'
import { useAuthStore } from '../store/authStore'
import { useNavigate } from 'react-router-dom'

interface SidebarProps {
  currentView: 'chat' | 'emails' | 'calendar'
  onViewChange: (view: 'chat' | 'emails' | 'calendar') => void
}

export default function Sidebar({ currentView, onViewChange }: SidebarProps) {
  const logout = useAuthStore((state) => state.logout)
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  const menuItems = [
    { id: 'chat' as const, icon: MessageSquare, label: 'Chat' },
    { id: 'emails' as const, icon: Mail, label: 'Emails' },
    { id: 'calendar' as const, icon: Calendar, label: 'Calendar' },
  ]

  return (
    <div className="w-64 bg-gray-900 text-white flex flex-col">
      <div className="p-4">
        <div className="flex items-center gap-2 mb-8">
          <div className="bg-blue-600 p-2 rounded-lg">
            <Mail className="w-6 h-6" />
          </div>
          <div>
            <h1 className="font-bold">Gmail AI</h1>
            <p className="text-xs text-gray-400">Organizer</p>
          </div>
        </div>

        <nav className="space-y-2">
          {menuItems.map((item) => {
            const Icon = item.icon
            const isActive = currentView === item.id

            return (
              <button
                key={item.id}
                onClick={() => onViewChange(item.id)}
                className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
                  isActive
                    ? 'bg-blue-600 text-white'
                    : 'text-gray-300 hover:bg-gray-800'
                }`}
              >
                <Icon className="w-5 h-5" />
                <span className="font-medium">{item.label}</span>
              </button>
            )
          })}
        </nav>
      </div>

      <div className="mt-auto p-4 space-y-2">
        <button className="w-full flex items-center gap-3 px-4 py-3 rounded-lg text-gray-300 hover:bg-gray-800 transition-colors">
          <Settings className="w-5 h-5" />
          <span className="font-medium">Settings</span>
        </button>

        <button
          onClick={handleLogout}
          className="w-full flex items-center gap-3 px-4 py-3 rounded-lg text-gray-300 hover:bg-gray-800 transition-colors"
        >
          <LogOut className="w-5 h-5" />
          <span className="font-medium">Logout</span>
        </button>

        <div className="pt-4 border-t border-gray-800">
          <p className="text-xs text-gray-500 text-center">
            Open Source • Privacy First
          </p>
        </div>
      </div>
    </div>
  )
}
