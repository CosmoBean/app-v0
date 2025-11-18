import { useState } from 'react'
import { useAuthStore } from '../store/authStore'
import ChatInterface from '../components/ChatInterface'
import EmailList from '../components/EmailList'
import CalendarView from '../components/CalendarView'
import Sidebar from '../components/Sidebar'
import Header from '../components/Header'

type View = 'chat' | 'emails' | 'calendar'

export default function DashboardPage() {
  const [currentView, setCurrentView] = useState<View>('chat')
  const userEmail = useAuthStore((state) => state.userEmail)

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex">
      <Sidebar currentView={currentView} onViewChange={setCurrentView} />

      <div className="flex-1 flex flex-col">
        <Header userEmail={userEmail} />

        <main className="flex-1 overflow-hidden">
          {currentView === 'chat' && <ChatInterface />}
          {currentView === 'emails' && <EmailList />}
          {currentView === 'calendar' && <CalendarView />}
        </main>
      </div>
    </div>
  )
}
