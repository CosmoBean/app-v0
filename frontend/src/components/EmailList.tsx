import { useState, useEffect } from 'react'
import { Mail, Archive, Trash2, Star, Loader2 } from 'lucide-react'
import { gmailAPI } from '../services/api'
import { Email } from '../types'
import { format } from 'date-fns'

export default function EmailList() {
  const [emails, setEmails] = useState<Email[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedEmail, setSelectedEmail] = useState<Email | null>(null)
  const [filter, setFilter] = useState<'all' | 'unread' | 'important'>('all')

  useEffect(() => {
    loadEmails()
  }, [filter])

  const loadEmails = async () => {
    setLoading(true)
    try {
      const query = filter === 'unread' ? 'is:unread' : filter === 'important' ? 'is:starred' : ''
      const response = await gmailAPI.getMessages({ query, max_results: 50 })
      setEmails(response.messages || [])
    } catch (error) {
      console.error('Error loading emails:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleArchive = async (emailId: string) => {
    try {
      await gmailAPI.archiveMessage(emailId)
      setEmails(emails.filter((e) => e.id !== emailId))
      if (selectedEmail?.id === emailId) {
        setSelectedEmail(null)
      }
    } catch (error) {
      console.error('Error archiving email:', error)
    }
  }

  const handleTrash = async (emailId: string) => {
    try {
      await gmailAPI.trashMessage(emailId)
      setEmails(emails.filter((e) => e.id !== emailId))
      if (selectedEmail?.id === emailId) {
        setSelectedEmail(null)
      }
    } catch (error) {
      console.error('Error trashing email:', error)
    }
  }

  return (
    <div className="h-full flex bg-white dark:bg-gray-800">
      {/* Email List */}
      <div className="w-1/3 border-r dark:border-gray-700 flex flex-col">
        <div className="p-4 border-b dark:border-gray-700">
          <div className="flex gap-2">
            <button
              onClick={() => setFilter('all')}
              className={`px-3 py-1 rounded text-sm ${
                filter === 'all'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300'
              }`}
            >
              All
            </button>
            <button
              onClick={() => setFilter('unread')}
              className={`px-3 py-1 rounded text-sm ${
                filter === 'unread'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300'
              }`}
            >
              Unread
            </button>
            <button
              onClick={() => setFilter('important')}
              className={`px-3 py-1 rounded text-sm ${
                filter === 'important'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300'
              }`}
            >
              Important
            </button>
          </div>
        </div>

        <div className="flex-1 overflow-y-auto">
          {loading ? (
            <div className="flex items-center justify-center h-32">
              <Loader2 className="w-6 h-6 animate-spin text-blue-600" />
            </div>
          ) : emails.length === 0 ? (
            <div className="p-8 text-center text-gray-500 dark:text-gray-400">
              <Mail className="w-12 h-12 mx-auto mb-2 opacity-50" />
              <p>No emails found</p>
            </div>
          ) : (
            emails.map((email) => (
              <div
                key={email.id}
                onClick={() => setSelectedEmail(email)}
                className={`p-4 border-b dark:border-gray-700 cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-700 ${
                  selectedEmail?.id === email.id ? 'bg-blue-50 dark:bg-blue-900' : ''
                }`}
              >
                <div className="flex items-start justify-between mb-1">
                  <p className="font-semibold text-sm text-gray-900 dark:text-white truncate">
                    {email.from}
                  </p>
                  {email.labels?.includes('STARRED') && (
                    <Star className="w-4 h-4 text-yellow-500" fill="currentColor" />
                  )}
                </div>
                <p className="font-medium text-sm text-gray-800 dark:text-gray-200 truncate">
                  {email.subject}
                </p>
                <p className="text-xs text-gray-600 dark:text-gray-400 truncate mt-1">
                  {email.snippet}
                </p>
                {email.category && (
                  <span className="inline-block mt-2 px-2 py-0.5 text-xs rounded bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200">
                    {email.category}
                  </span>
                )}
              </div>
            ))
          )}
        </div>
      </div>

      {/* Email Detail */}
      <div className="flex-1 flex flex-col">
        {selectedEmail ? (
          <>
            <div className="p-4 border-b dark:border-gray-700">
              <div className="flex items-start justify-between mb-4">
                <div>
                  <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
                    {selectedEmail.subject}
                  </h2>
                  <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                    From: {selectedEmail.from}
                  </p>
                  <p className="text-xs text-gray-500 dark:text-gray-500 mt-1">
                    {selectedEmail.date}
                  </p>
                </div>
                <div className="flex gap-2">
                  <button
                    onClick={() => handleArchive(selectedEmail.id)}
                    className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded transition-colors"
                    title="Archive"
                  >
                    <Archive className="w-5 h-5 text-gray-600 dark:text-gray-400" />
                  </button>
                  <button
                    onClick={() => handleTrash(selectedEmail.id)}
                    className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded transition-colors"
                    title="Delete"
                  >
                    <Trash2 className="w-5 h-5 text-gray-600 dark:text-gray-400" />
                  </button>
                </div>
              </div>

              {selectedEmail.summary && (
                <div className="bg-blue-50 dark:bg-blue-900 p-3 rounded-lg">
                  <p className="text-sm font-semibold text-blue-900 dark:text-blue-100 mb-1">
                    AI Summary:
                  </p>
                  <p className="text-sm text-blue-800 dark:text-blue-200">
                    {selectedEmail.summary}
                  </p>
                </div>
              )}
            </div>

            <div className="flex-1 overflow-y-auto p-4">
              <div className="prose dark:prose-invert max-w-none">
                <p className="whitespace-pre-wrap text-gray-900 dark:text-gray-100">
                  {selectedEmail.body_text}
                </p>
              </div>
            </div>
          </>
        ) : (
          <div className="flex-1 flex items-center justify-center text-gray-500 dark:text-gray-400">
            <div className="text-center">
              <Mail className="w-16 h-16 mx-auto mb-4 opacity-50" />
              <p>Select an email to view</p>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
