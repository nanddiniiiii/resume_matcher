'use client'

import { useState, useEffect } from 'react'
import { useAuth } from '@/contexts/AuthContext'
import toast from 'react-hot-toast'

interface ScraperStatus {
  total_jobs: number
  active_jobs: number
  expired_jobs: number
  jobs_by_source: { [key: string]: number }
  jobs_by_type: { [key: string]: number }
  last_scrape: string | null
  sources_available: string[]
}

export default function ScraperAdminPage() {
  const [status, setStatus] = useState<ScraperStatus | null>(null)
  const [loading, setLoading] = useState(true)
  const [scraping, setScraping] = useState(false)
  const [markingExpired, setMarkingExpired] = useState(false)
  const { token } = useAuth()

  const fetchStatus = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/scraper/status', {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      })

      if (response.ok) {
        const data = await response.json()
        setStatus(data)
      } else {
        toast.error('Failed to fetch scraper status')
      }
    } catch (error) {
      console.error('Status fetch error:', error)
      toast.error('Error fetching status')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchStatus()
  }, [])

  const handleRunScraper = async () => {
    setScraping(true)
    try {
      const response = await fetch('http://localhost:8000/api/scraper/run', {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      })

      if (response.ok) {
        const data = await response.json()
        toast.success(data.message)
        // Refresh status after a delay to allow scraping to complete
        setTimeout(() => fetchStatus(), 3000)
      } else {
        const error = await response.json()
        toast.error(error.detail || 'Failed to run scraper')
      }
    } catch (error) {
      console.error('Scraper error:', error)
      toast.error('Error running scraper')
    } finally {
      setScraping(false)
    }
  }

  const handleMarkExpired = async () => {
    setMarkingExpired(true)
    try {
      const response = await fetch('http://localhost:8000/api/scraper/mark-expired', {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      })

      if (response.ok) {
        const data = await response.json()
        toast.success(`Marked ${data.marked_expired} jobs as expired`)
        fetchStatus()
      } else {
        const error = await response.json()
        toast.error(error.detail || 'Failed to mark expired jobs')
      }
    } catch (error) {
      console.error('Mark expired error:', error)
      toast.error('Error marking expired jobs')
    } finally {
      setMarkingExpired(false)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            <p className="mt-4 text-gray-600">Loading scraper status...</p>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Job Scraper Control Panel</h1>
          <p className="mt-2 text-gray-600">
            Manage job scraping from external sources and monitor data freshness
          </p>
        </div>

        {/* Action Buttons */}
        <div className="mb-8 flex gap-4">
          <button
            onClick={handleRunScraper}
            disabled={scraping}
            className={`px-6 py-3 bg-blue-600 text-white rounded-lg font-semibold 
              ${scraping ? 'opacity-50 cursor-not-allowed' : 'hover:bg-blue-700'} 
              transition-colors`}
          >
            {scraping ? (
              <span className="flex items-center">
                <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Scraping...
              </span>
            ) : (
              '🚀 Run Scraper'
            )}
          </button>

          <button
            onClick={handleMarkExpired}
            disabled={markingExpired}
            className={`px-6 py-3 bg-orange-600 text-white rounded-lg font-semibold 
              ${markingExpired ? 'opacity-50 cursor-not-allowed' : 'hover:bg-orange-700'} 
              transition-colors`}
          >
            {markingExpired ? 'Marking...' : '🗑️ Mark Expired Jobs'}
          </button>

          <button
            onClick={fetchStatus}
            className="px-6 py-3 bg-gray-200 text-gray-700 rounded-lg font-semibold hover:bg-gray-300 transition-colors"
          >
            🔄 Refresh Status
          </button>
        </div>

        {/* Status Overview */}
        {status && (
          <div className="space-y-6">
            {/* Summary Cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="bg-white rounded-lg shadow p-6">
                <h3 className="text-sm font-medium text-gray-500 uppercase tracking-wide">Total Jobs</h3>
                <p className="mt-2 text-4xl font-bold text-gray-900">{status.total_jobs}</p>
              </div>

              <div className="bg-white rounded-lg shadow p-6">
                <h3 className="text-sm font-medium text-gray-500 uppercase tracking-wide">Active Jobs</h3>
                <p className="mt-2 text-4xl font-bold text-green-600">{status.active_jobs}</p>
              </div>

              <div className="bg-white rounded-lg shadow p-6">
                <h3 className="text-sm font-medium text-gray-500 uppercase tracking-wide">Expired Jobs</h3>
                <p className="mt-2 text-4xl font-bold text-red-600">{status.expired_jobs}</p>
              </div>
            </div>

            {/* Last Scrape Time */}
            {status.last_scrape && (
              <div className="bg-blue-50 border-l-4 border-blue-400 p-4">
                <p className="text-sm text-blue-700">
                  <span className="font-semibold">Last Scrape:</span> {new Date(status.last_scrape).toLocaleString()}
                </p>
              </div>
            )}

            {/* Jobs by Source */}
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-xl font-bold text-gray-900 mb-4">Jobs by Source</h2>
              <div className="space-y-3">
                {Object.entries(status.jobs_by_source).map(([source, count]) => (
                  <div key={source} className="flex items-center justify-between">
                    <div className="flex items-center">
                      <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-blue-100 text-blue-800">
                        {source || 'manual'}
                      </span>
                    </div>
                    <span className="text-2xl font-bold text-gray-700">{count}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Jobs by Type */}
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-xl font-bold text-gray-900 mb-4">Jobs by Type</h2>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {Object.entries(status.jobs_by_type).map(([type, count]) => (
                  <div key={type} className="text-center p-4 bg-gray-50 rounded-lg">
                    <p className="text-sm font-medium text-gray-600">{type}</p>
                    <p className="mt-2 text-2xl font-bold text-gray-900">{count}</p>
                  </div>
                ))}
              </div>
            </div>

            {/* Available Sources */}
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-xl font-bold text-gray-900 mb-4">Available Scraper Sources</h2>
              <div className="flex flex-wrap gap-2">
                {status.sources_available.map((source) => (
                  <span
                    key={source}
                    className="inline-flex items-center px-4 py-2 rounded-lg text-sm font-medium bg-green-100 text-green-800"
                  >
                    ✓ {source}
                  </span>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
