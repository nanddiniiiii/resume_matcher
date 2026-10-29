'use client'

import { API_BASE_URL } from '@/lib/config'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { JobMatch } from '@/lib/types'
import { useAuth } from '@/contexts/AuthContext'
import toast from 'react-hot-toast'
import JobFreshnessBadge from './JobFreshnessBadge'
import JobSourceBadge from './JobSourceBadge'
import ResumeTips from './ResumeTips'

interface JobCardProps {
  match: JobMatch
  rank: number
  resumeId: number
}

export default function JobCard({ match, rank, resumeId }: JobCardProps) {
  const [expanded, setExpanded] = useState(false)
  const [savingJob, setSavingJob] = useState(false)
  const [trackingApp, setTrackingApp] = useState(false)
  const { job, explanation, matching_skills, missing_skills } = match
  const { token } = useAuth()
  const router = useRouter()

  const handleSaveJob = async () => {
    setSavingJob(true)
    try {
      const response = await fetch(`${API_BASE_URL}/api/jobs/${job.id}/save`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      })

      if (response.ok) {
        toast.success('Job saved successfully!')
      } else {
        const error = await response.json()
        toast.error(error.detail || 'Failed to save job')
      }
    } catch (error) {
      console.error('Save error:', error)
      toast.error('Error saving job')
    } finally {
      setSavingJob(false)
    }
  }

  const handleTrackApplication = async () => {
    setTrackingApp(true)
    try {
      const response = await fetch(`${API_BASE_URL}/api/applications/`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          job_id: job.id,
          resume_id: resumeId,
        }),
      })

      if (response.ok) {
        toast.success('Application tracked successfully!')
        router.push('/applications')
      } else {
        const error = await response.json()
        toast.error(error.detail || 'Failed to track application')
      }
    } catch (error) {
      console.error('Track application error:', error)
      toast.error('Error tracking application')
    } finally {
      setTrackingApp(false)
    }
  }

  // Get quality badge color
  const getQualityColor = (quality: string) => {
    switch (quality) {
      case 'Excellent':
        return 'bg-green-100 text-green-800 border-green-300'
      case 'Good':
        return 'bg-blue-100 text-blue-800 border-blue-300'
      case 'Fair':
        return 'bg-yellow-100 text-yellow-800 border-yellow-300'
      default:
        return 'bg-gray-100 text-gray-800 border-gray-300'
    }
  }

  // Get score color
  const getScoreColor = (score: number) => {
    if (score >= 70) return 'text-green-600'
    if (score >= 50) return 'text-blue-600'
    return 'text-yellow-600'
  }

  return (
    <div className="bg-white rounded-xl shadow-md border border-gray-200 hover:shadow-lg transition-shadow overflow-hidden">
      {/* Card Header */}
      <div className="p-6">
        <div className="flex items-start justify-between mb-4">
          <div className="flex-1">
            <div className="flex items-center gap-3 mb-2">
              <span className="flex items-center justify-center w-8 h-8 rounded-full bg-primary-100 text-primary-700 font-bold text-sm">
                #{rank}
              </span>
              <h3 className="text-2xl font-bold text-gray-900">{job.title}</h3>
            </div>
            <p className="text-lg text-gray-600 mb-2">{job.company}</p>
            <div className="flex flex-wrap items-center gap-2 text-sm text-gray-500">
              {job.location && (
                <span className="flex items-center">
                  <svg className="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M5.05 4.05a7 7 0 119.9 9.9L10 18.9l-4.95-4.95a7 7 0 010-9.9zM10 11a2 2 0 100-4 2 2 0 000 4z" clipRule="evenodd" />
                  </svg>
                  {job.location}
                </span>
              )}
              {job.job_type && (
                <span className="px-2 py-1 bg-gray-100 rounded-full capitalize">
                  {job.job_type}
                </span>
              )}
              <JobFreshnessBadge
                scrapedAt={job.scraped_at || null}
                isActive={job.is_active !== false}
              />
              <JobSourceBadge
                source={job.source || null}
                sourceUrl={job.source_url || null}
              />
            </div>
          </div>
          <div className="text-right ml-4">
            <div className={`text-4xl font-bold ${getScoreColor(explanation.overall_score)}`}>
              {Math.round(explanation.overall_score)}%
            </div>
            <div className={`mt-2 px-3 py-1 border rounded-full text-sm font-medium ${getQualityColor(explanation.match_quality)}`}>
              {explanation.match_quality} Match
            </div>
          </div>
        </div>

        {/* Recommendation */}
        <div className="mb-4 p-4 bg-primary-50 border border-primary-200 rounded-lg">
          <p className="text-primary-900 font-medium">{explanation.recommendation}</p>
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-2 gap-4 mb-4">
          <div className="flex items-center">
            <svg className="w-5 h-5 text-green-500 mr-2" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
            </svg>
            <span className="text-sm">
              <span className="font-semibold text-green-700">{matching_skills.length}</span>
              <span className="text-gray-600"> matching skills</span>
            </span>
          </div>
          <div className="flex items-center">
            <svg className="w-5 h-5 text-yellow-500 mr-2" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
            </svg>
            <span className="text-sm">
              <span className="font-semibold text-yellow-700">{missing_skills.length}</span>
              <span className="text-gray-600"> skills to learn</span>
            </span>
          </div>
        </div>

        {/* Toggle Details Button */}
        <button
          onClick={() => setExpanded(!expanded)}
          className="w-full flex items-center justify-center py-2 px-4 bg-gray-50 hover:bg-gray-100 rounded-lg transition-colors mb-4"
        >
          <span className="text-sm font-medium text-gray-700">
            {expanded ? 'Hide Details' : 'Show Details'}
          </span>
          <svg
            className={`w-5 h-5 ml-2 text-gray-500 transform transition-transform ${expanded ? 'rotate-180' : ''}`}
            fill="currentColor"
            viewBox="0 0 20 20"
          >
            <path fillRule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clipRule="evenodd" />
          </svg>
        </button>

        {/* Action Buttons */}
        <div className="space-y-3">
          <div className="flex gap-3">
            <button
              onClick={handleSaveJob}
              disabled={savingJob}
              className="flex-1 px-4 py-3 border-2 border-purple-600 text-purple-600 font-semibold rounded-lg hover:bg-purple-50 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {savingJob ? 'Saving...' : '⭐ Save Job'}
            </button>
            <button
              onClick={handleTrackApplication}
              disabled={trackingApp}
              className="flex-1 px-4 py-3 bg-gradient-to-r from-purple-600 to-pink-600 text-white font-semibold rounded-lg hover:from-purple-700 hover:to-pink-700 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {trackingApp ? 'Tracking...' : '📋 Track Application'}
            </button>
          </div>
          <div className="flex gap-3">
            <ResumeTips resumeId={resumeId} jobId={job.id} jobTitle={job.title} />
            {job.source_url && (
              <a
                href={job.source_url}
                target="_blank"
                rel="noopener noreferrer"
                className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm font-medium text-center"
              >
                🔗 Apply on Company Site
              </a>
            )}
          </div>
        </div>
      </div>

      {/* Expanded Details */}
      {expanded && (
        <div className="border-t border-gray-200 bg-gray-50 p-6">
          {/* Job Description */}
          <div className="mb-6">
            <h4 className="text-lg font-semibold text-gray-900 mb-2">Job Description</h4>
            <p className="text-gray-700 text-sm leading-relaxed">{job.description}</p>
          </div>

          {/* Why This Matches */}
          <div className="mb-6">
            <h4 className="text-lg font-semibold text-gray-900 mb-2">Why This Job Matches</h4>
            <p className="text-gray-700 text-sm">{explanation.why_this_matches}</p>
            <p className="text-gray-600 text-sm mt-2">{explanation.skill_analysis}</p>
          </div>

          {/* Your Strengths */}
          <div className="mb-6">
            <h4 className="text-lg font-semibold text-gray-900 mb-3">
              ✅ Your Strengths ({matching_skills.length})
            </h4>
            <div className="flex flex-wrap gap-2">
              {matching_skills.slice(0, 10).map((skill, idx) => (
                <span
                  key={idx}
                  className="px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm font-medium"
                >
                  {skill}
                </span>
              ))}
            </div>
          </div>

          {/* Skills to Improve */}
          {missing_skills.length > 0 && (
            <div className="mb-6">
              <h4 className="text-lg font-semibold text-gray-900 mb-3">
                📚 Skills to Develop ({missing_skills.length})
              </h4>
              <div className="flex flex-wrap gap-2">
                {missing_skills.slice(0, 10).map((skill, idx) => (
                  <span
                    key={idx}
                    className="px-3 py-1 bg-yellow-100 text-yellow-800 rounded-full text-sm font-medium"
                  >
                    {skill}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* All Required Skills */}
          <div>
            <h4 className="text-lg font-semibold text-gray-900 mb-3">
              All Required Skills
            </h4>
            <div className="flex flex-wrap gap-2">
              {job.required_skills.map((skill, idx) => (
                <span
                  key={idx}
                  className="px-3 py-1 bg-gray-200 text-gray-700 rounded-full text-sm"
                >
                  {skill}
                </span>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
