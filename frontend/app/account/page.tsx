'use client'

import { useAuth } from '@/contexts/AuthContext'
import { useRouter } from 'next/navigation'
import { useEffect, useState } from 'react'
import Header from '@/components/Header'
import { toast } from 'react-hot-toast'

interface UserStats {
  total_resumes: number
  total_matches: number
  total_saved_jobs: number
  total_applications: number
  application_breakdown: {
    applied?: number
    interviewing?: number
    accepted?: number
    rejected?: number
  }
  recent_activity: {
    last_resume_upload: string | null
    last_application: string | null
  }
}

export default function AccountPage() {
  const { user, token, loading, isAuthenticated } = useAuth()
  const router = useRouter()
  const [isEditing, setIsEditing] = useState(false)
  const [name, setName] = useState('')
  const [stats, setStats] = useState<UserStats | null>(null)
  const [loadingStats, setLoadingStats] = useState(true)

  useEffect(() => {
    if (!loading && !isAuthenticated) {
      router.push('/login')
    }
    if (user) {
      setName(user.name || '')
      fetchStats()
    }
  }, [loading, isAuthenticated, router, user])

  const fetchStats = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/users/stats', {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      })
      if (response.ok) {
        const data = await response.json()
        setStats(data)
      }
    } catch (error) {
      console.error('Failed to fetch stats:', error)
    } finally {
      setLoadingStats(false)
    }
  }

  const handleUpdateName = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/auth/me', {
        method: 'PUT',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ name }),
      })
      if (response.ok) {
        toast.success('Name updated successfully!')
        setIsEditing(false)
      } else {
        toast.error('Failed to update name')
      }
    } catch (error) {
      toast.error('Failed to update name')
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600"></div>
      </div>
    )
  }

  if (!user) return null

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 transition-colors">
      <Header />
      
      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl overflow-hidden transition-colors">
          {/* Header */}
          <div className="bg-gradient-to-r from-purple-600 to-pink-600 px-8 py-12">
            <div className="flex items-center space-x-4">
              <div className="w-20 h-20 bg-white rounded-full flex items-center justify-center text-purple-600 text-3xl font-bold shadow-lg">
                {user.name?.[0]?.toUpperCase() || user.email?.[0]?.toUpperCase()}
              </div>
              <div className="text-white">
                <h1 className="text-3xl font-bold">{user.name || 'User'}</h1>
                <p className="text-purple-100 mt-1">{user.email}</p>
              </div>
            </div>
          </div>

          {/* Content */}
          <div className="px-8 py-8">
            <div className="space-y-6">
              {/* Account Information */}
              <div>
                <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">Account Information</h2>
                
                <div className="space-y-4">
                  {/* Email */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Email Address
                    </label>
                    <div className="px-4 py-3 bg-gray-50 dark:bg-gray-700 rounded-lg border border-gray-200 dark:border-gray-600">
                      <p className="text-gray-900 dark:text-white">{user.email}</p>
                    </div>
                    <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">Email cannot be changed</p>
                  </div>

                  {/* Name */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Full Name
                    </label>
                    {isEditing ? (
                      <div className="space-y-2">
                        <input
                          type="text"
                          value={name}
                          onChange={(e) => setName(e.target.value)}
                          className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
                          placeholder="Enter your name"
                        />
                        <div className="flex space-x-2">
                          <button
                            onClick={handleUpdateName}
                            className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
                          >
                            Save
                          </button>
                          <button
                            onClick={() => {
                              setName(user.name || '')
                              setIsEditing(false)
                            }}
                            className="px-4 py-2 bg-gray-200 dark:bg-gray-600 text-gray-700 dark:text-gray-200 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-500 transition-colors"
                          >
                            Cancel
                          </button>
                        </div>
                      </div>
                    ) : (
                      <div className="flex items-center justify-between px-4 py-3 bg-gray-50 dark:bg-gray-700 rounded-lg border border-gray-200 dark:border-gray-600">
                        <p className="text-gray-900 dark:text-white">{user.name || 'Not set'}</p>
                        <button
                          onClick={() => setIsEditing(true)}
                          className="text-purple-600 dark:text-purple-400 hover:text-purple-700 dark:hover:text-purple-300 text-sm font-medium"
                        >
                          Edit
                        </button>
                      </div>
                    )}
                  </div>

                  {/* Account Created */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Member Since
                    </label>
                    <div className="px-4 py-3 bg-gray-50 dark:bg-gray-700 rounded-lg border border-gray-200 dark:border-gray-600">
                      <p className="text-gray-900 dark:text-white">
                        {new Date(user.created_at || Date.now()).toLocaleDateString('en-US', {
                          year: 'numeric',
                          month: 'long',
                          day: 'numeric'
                        })}
                      </p>
                    </div>
                  </div>
                </div>
              </div>

              {/* Activity Summary */}
              <div className="pt-6 border-t border-gray-200 dark:border-gray-700">
                <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">Activity Statistics</h2>
                {loadingStats ? (
                  <div className="text-center py-8">
                    <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600"></div>
                  </div>
                ) : stats ? (
                  <>
                    <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
                      <div className="bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-900/20 dark:to-blue-800/20 p-6 rounded-lg border border-blue-200 dark:border-blue-800">
                        <div className="text-3xl mb-2">📄</div>
                        <p className="text-2xl font-bold text-blue-900 dark:text-blue-100">{stats.total_resumes}</p>
                        <p className="text-sm text-blue-700 dark:text-blue-300">Resumes Uploaded</p>
                      </div>
                      <div className="bg-gradient-to-br from-purple-50 to-purple-100 dark:from-purple-900/20 dark:to-purple-800/20 p-6 rounded-lg border border-purple-200 dark:border-purple-800">
                        <div className="text-3xl mb-2">💼</div>
                        <p className="text-2xl font-bold text-purple-900 dark:text-purple-100">{stats.total_matches}</p>
                        <p className="text-sm text-purple-700 dark:text-purple-300">Job Matches</p>
                      </div>
                      <div className="bg-gradient-to-br from-pink-50 to-pink-100 dark:from-pink-900/20 dark:to-pink-800/20 p-6 rounded-lg border border-pink-200 dark:border-pink-800">
                        <div className="text-3xl mb-2">⭐</div>
                        <p className="text-2xl font-bold text-pink-900 dark:text-pink-100">{stats.total_saved_jobs}</p>
                        <p className="text-sm text-pink-700 dark:text-pink-300">Saved Jobs</p>
                      </div>
                      <div className="bg-gradient-to-br from-green-50 to-green-100 dark:from-green-900/20 dark:to-green-800/20 p-6 rounded-lg border border-green-200 dark:border-green-800">
                        <div className="text-3xl mb-2">📋</div>
                        <p className="text-2xl font-bold text-green-900 dark:text-green-100">{stats.total_applications}</p>
                        <p className="text-sm text-green-700 dark:text-green-300">Applications</p>
                      </div>
                    </div>

                    {/* Application Breakdown */}
                    {stats.total_applications > 0 && (
                      <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-6 border border-gray-200 dark:border-gray-600">
                        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Application Status</h3>
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                          <div>
                            <p className="text-2xl font-bold text-blue-600">{stats.application_breakdown.applied || 0}</p>
                            <p className="text-sm text-gray-600 dark:text-gray-400">Applied</p>
                          </div>
                          <div>
                            <p className="text-2xl font-bold text-yellow-600">{stats.application_breakdown.interviewing || 0}</p>
                            <p className="text-sm text-gray-600 dark:text-gray-400">Interviewing</p>
                          </div>
                          <div>
                            <p className="text-2xl font-bold text-green-600">{stats.application_breakdown.accepted || 0}</p>
                            <p className="text-sm text-gray-600 dark:text-gray-400">Accepted</p>
                          </div>
                          <div>
                            <p className="text-2xl font-bold text-red-600">{stats.application_breakdown.rejected || 0}</p>
                            <p className="text-sm text-gray-600 dark:text-gray-400">Rejected</p>
                          </div>
                        </div>
                      </div>
                    )}

                    {/* Recent Activity */}
                    <div className="mt-6 bg-gray-50 dark:bg-gray-700 rounded-lg p-6 border border-gray-200 dark:border-gray-600">
                      <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Recent Activity</h3>
                      <div className="space-y-2 text-sm text-gray-600 dark:text-gray-400">
                        <p>
                          <strong>Last Resume Upload:</strong>{' '}
                          {stats.recent_activity.last_resume_upload
                            ? new Date(stats.recent_activity.last_resume_upload).toLocaleString()
                            : 'Never'}
                        </p>
                        <p>
                          <strong>Last Application:</strong>{' '}
                          {stats.recent_activity.last_application
                            ? new Date(stats.recent_activity.last_application).toLocaleString()
                            : 'Never'}
                        </p>
                      </div>
                    </div>
                  </>
                ) : null}
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}
