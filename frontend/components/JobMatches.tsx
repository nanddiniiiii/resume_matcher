'use client'

import { useState, useEffect } from 'react'
import { matchAPI } from '@/lib/api'
import { JobMatch, JobMatchListResponse } from '@/lib/types'
import JobCard from './JobCard'

interface JobMatchesProps {
  resumeId: number
}

export default function JobMatches({ resumeId }: JobMatchesProps) {
  const [matches, setMatches] = useState<JobMatch[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [totalMatches, setTotalMatches] = useState(0)

  useEffect(() => {
    loadMatches()
  }, [resumeId])

  const loadMatches = async () => {
    setLoading(true)
    setError(null)

    try {
      const data: JobMatchListResponse = await matchAPI.getMatches(resumeId, 10)
      setMatches(data.matches)
      setTotalMatches(data.total_matches)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load job matches')
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-center">
          <svg className="animate-spin h-12 w-12 text-primary-600 mx-auto mb-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <p className="text-lg text-gray-600">Analyzing and matching jobs...</p>
          <p className="text-sm text-gray-500 mt-2">This may take a few moments</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-6">
        <div className="flex">
          <svg className="w-6 h-6 text-red-600 mr-3" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
          </svg>
          <div>
            <h3 className="text-lg font-medium text-red-800">Error Loading Matches</h3>
            <p className="text-sm text-red-700 mt-1">{error}</p>
            <button
              onClick={loadMatches}
              className="mt-3 text-sm font-medium text-red-600 hover:text-red-500"
            >
              Try Again
            </button>
          </div>
        </div>
      </div>
    )
  }

  if (matches.length === 0) {
    return (
      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6 text-center">
        <svg className="w-12 h-12 text-yellow-600 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
        </svg>
        <h3 className="text-lg font-medium text-yellow-900 mb-2">No Matches Found</h3>
        <p className="text-yellow-700">
          We couldn't find any jobs matching your resume. Try uploading a different resume or check back later for new opportunities.
        </p>
      </div>
    )
  }

  return (
    <div>
      {/* Header */}
      <div className="mb-8">
        <h2 className="text-3xl font-bold text-gray-900 mb-2">
          Your Top Job Matches
        </h2>
        <p className="text-lg text-gray-600">
          Found {totalMatches} {totalMatches === 1 ? 'job' : 'jobs'} that match your profile
        </p>
      </div>

      {/* Match Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
        <div className="bg-green-50 border border-green-200 rounded-lg p-4">
          <div className="flex items-center">
            <div className="text-2xl mr-3">🎯</div>
            <div>
              <p className="text-sm text-green-600 font-medium">Excellent Matches</p>
              <p className="text-2xl font-bold text-green-900">
                {matches.filter(m => m.explanation.match_quality === 'Excellent').length}
              </p>
            </div>
          </div>
        </div>
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-center">
            <div className="text-2xl mr-3">👍</div>
            <div>
              <p className="text-sm text-blue-600 font-medium">Good Matches</p>
              <p className="text-2xl font-bold text-blue-900">
                {matches.filter(m => m.explanation.match_quality === 'Good').length}
              </p>
            </div>
          </div>
        </div>
        <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
          <div className="flex items-center">
            <div className="text-2xl mr-3">📈</div>
            <div>
              <p className="text-sm text-purple-600 font-medium">Average Score</p>
              <p className="text-2xl font-bold text-purple-900">
                {Math.round(matches.reduce((acc, m) => acc + m.explanation.overall_score, 0) / matches.length)}%
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Job Cards */}
      <div className="space-y-6">
        {matches.map((match, index) => (
          <JobCard key={match.job.id} match={match} rank={index + 1} />
        ))}
      </div>
    </div>
  )
}
