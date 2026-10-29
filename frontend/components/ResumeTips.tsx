'use client'

import { API_BASE_URL } from '@/lib/config'

import { useState } from 'react'
import { useAuth } from '@/contexts/AuthContext'
import toast from 'react-hot-toast'

interface ResumeTipsProps {
  resumeId: number
  jobId: number
  jobTitle: string
}

interface FullAnalysis {
  ats_score: number
  score_interpretation: string
  missing_keywords: string[]
  weak_areas: Array<{ area: string; issue: string; severity: string }>
  suggestions: Array<{ category: string; description: string; action: string; priority: string }>
  keyword_analysis: Record<string, { count: number; status: string }>
  skill_match_rate: number
  recommended_additions: string[]
}

export default function ResumeTips({ jobId, jobTitle, resumeId }: ResumeTipsProps) {
  const [showModal, setShowModal] = useState(false)
  const [quickTips, setQuickTips] = useState<string[]>([])
  const [fullAnalysis, setFullAnalysis] = useState<FullAnalysis | null>(null)
  const [loadingTips, setLoadingTips] = useState(false)
  const [loadingAnalysis, setLoadingAnalysis] = useState(false)
  const { token } = useAuth()

  const fetchQuickTips = async () => {
    setLoadingTips(true)
    try {
      const response = await fetch(
        `${API_BASE_URL}/api/resume-analyzer/quick-tips/${jobId}`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      )

      if (response.ok) {
        const data = await response.json()
        setQuickTips(data.tips)
      } else {
        toast.error('Failed to fetch quick tips')
      }
    } catch (error) {
      console.error('Quick tips error:', error)
      toast.error('Error fetching tips')
    } finally {
      setLoadingTips(false)
    }
  }

  const fetchFullAnalysis = async () => {
    setLoadingAnalysis(true)
    try {
      const response = await fetch(`${API_BASE_URL}/api/resume-analyzer/analyze`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ job_id: jobId, resume_id: resumeId }),
      })

      if (response.ok) {
        const data = await response.json()
        setFullAnalysis(data)
        setShowModal(true)
      } else {
        const error = await response.json()
        toast.error(error.detail || 'Failed to analyze resume')
      }
    } catch (error) {
      console.error('Analysis error:', error)
      toast.error('Error analyzing resume')
    } finally {
      setLoadingAnalysis(false)
    }
  }

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600'
    if (score >= 60) return 'text-yellow-600'
    return 'text-red-600'
  }

  const getScoreBgColor = (score: number) => {
    if (score >= 80) return 'bg-green-100'
    if (score >= 60) return 'bg-yellow-100'
    return 'bg-red-100'
  }

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high':
        return 'bg-red-100 text-red-800'
      case 'medium':
        return 'bg-yellow-100 text-yellow-800'
      case 'low':
        return 'bg-blue-100 text-blue-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  return (
    <>
      {/* Quick Tips Button */}
      <button
        onClick={fetchQuickTips}
        disabled={loadingTips}
        className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors text-sm font-medium"
      >
        {loadingTips ? 'Loading...' : '💡 Resume Tips'}
      </button>

      {/* Full Analysis Button */}
      <button
        onClick={fetchFullAnalysis}
        disabled={loadingAnalysis}
        className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors text-sm font-medium"
      >
        {loadingAnalysis ? 'Analyzing...' : '📊 Full Analysis'}
      </button>

      {/* Quick Tips Display */}
      {quickTips.length > 0 && !showModal && (
        <div className="mt-4 p-4 bg-purple-50 border border-purple-200 rounded-lg">
          <h4 className="font-semibold text-purple-900 mb-2">Quick Tips:</h4>
          <ul className="space-y-2">
            {quickTips.map((tip, index) => (
              <li key={index} className="flex items-start">
                <span className="text-sm text-gray-700">{tip}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Full Analysis Modal */}
      {showModal && fullAnalysis && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            {/* Modal Header */}
            <div className="sticky top-0 bg-white border-b border-gray-200 px-6 py-4 flex justify-between items-center">
              <h2 className="text-2xl font-bold text-gray-900">Resume Analysis for {jobTitle}</h2>
              <button
                onClick={() => setShowModal(false)}
                className="text-gray-400 hover:text-gray-600 text-2xl font-bold"
              >
                ×
              </button>
            </div>

            <div className="p-6 space-y-6">
              {/* ATS Score */}
              <div className={`p-6 rounded-lg ${getScoreBgColor(fullAnalysis.ats_score)}`}>
                <div className="flex items-center justify-between mb-2">
                  <h3 className="text-lg font-bold text-gray-900">Resume relevance score</h3>
                  <span className={`text-5xl font-bold ${getScoreColor(fullAnalysis.ats_score)}`}>
                    {fullAnalysis.ats_score}
                  </span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-3">
                  <div
                    className={`h-3 rounded-full ${fullAnalysis.ats_score >= 80 ? 'bg-green-600' : fullAnalysis.ats_score >= 60 ? 'bg-yellow-600' : 'bg-red-600'}`}
                    style={{ width: `${fullAnalysis.ats_score}%` }}
                  ></div>
                </div>
                <p className="mt-2 text-sm text-gray-700">{fullAnalysis.score_interpretation}</p>
                <p className="mt-1 text-xs text-gray-600">Heuristic feedback, not a hiring probability or an employer ATS result.</p>
              </div>

              {/* Skill Match Rate */}
              <div className="bg-blue-50 p-4 rounded-lg">
                <h4 className="font-semibold text-blue-900 mb-2">Skill Match Rate</h4>
                <div className="flex items-center">
                  <span className="text-3xl font-bold text-blue-600">{fullAnalysis.skill_match_rate}%</span>
                  <span className="ml-2 text-sm text-gray-600">of required skills matched</span>
                </div>
              </div>

              {/* Missing Keywords */}
              {fullAnalysis.missing_keywords.length > 0 && (
                <div>
                  <h3 className="text-lg font-bold text-gray-900 mb-3">Missing Keywords</h3>
                  <div className="flex flex-wrap gap-2">
                    {fullAnalysis.missing_keywords.map((keyword, index) => (
                      <span key={index} className="px-3 py-1 bg-red-100 text-red-800 rounded-full text-sm font-medium">
                        {keyword}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Weak Areas */}
              {fullAnalysis.weak_areas.length > 0 && (
                <div>
                  <h3 className="text-lg font-bold text-gray-900 mb-3">Weak Areas to Improve</h3>
                  <ul className="space-y-2">
                    {fullAnalysis.weak_areas.map((area, index) => (
                      <li key={index} className="flex items-start">
                        <span className="text-red-500 mr-2">⚠️</span>
                        <span className="text-gray-700">{area.issue}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Detailed Suggestions */}
              <div>
                <h3 className="text-lg font-bold text-gray-900 mb-3">Actionable Suggestions</h3>
                <div className="space-y-3">
                  {fullAnalysis.suggestions.map((suggestion, index) => (
                    <div key={index} className="border-l-4 border-indigo-500 bg-gray-50 p-4">
                      <div className="flex items-center mb-1">
                        <span className={`px-2 py-0.5 rounded text-xs font-medium mr-2 ${getPriorityColor(suggestion.priority)}`}>
                          {suggestion.priority}
                        </span>
                        <span className="font-semibold text-gray-900">{suggestion.category}</span>
                      </div>
                      <p className="text-sm text-gray-700">{suggestion.description} {suggestion.action}</p>
                    </div>
                  ))}
                </div>
              </div>

              {/* Recommended Additions */}
              {fullAnalysis.recommended_additions.length > 0 && (
                <div>
                  <h3 className="text-lg font-bold text-gray-900 mb-3">Quick Additions</h3>
                  <ul className="grid grid-cols-1 md:grid-cols-2 gap-2">
                    {fullAnalysis.recommended_additions.map((addition, index) => (
                      <li key={index} className="flex items-start bg-green-50 p-3 rounded-lg">
                        <span className="text-green-600 mr-2">✓</span>
                        <span className="text-sm text-gray-700">{addition}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Keyword Analysis */}
              <div className="bg-gray-50 p-4 rounded-lg">
                <h3 className="text-lg font-bold text-gray-900 mb-3">Keyword Coverage</h3>
                <div className="grid grid-cols-2 gap-4 mb-4">
                  <div>
                    <p className="text-sm text-gray-600">Total Keywords</p>
                    <p className="text-2xl font-bold text-gray-900">{Object.keys(fullAnalysis.keyword_analysis).length}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Matched Keywords</p>
                    <p className="text-2xl font-bold text-green-600">{Object.values(fullAnalysis.keyword_analysis).filter(item => item.count > 0).length}</p>
                  </div>
                </div>
                {Object.keys(fullAnalysis.keyword_analysis).length > 0 && (
                  <div>
                    <p className="text-sm font-medium text-gray-700 mb-2">Keyword Frequency:</p>
                    <div className="flex flex-wrap gap-2">
                      {Object.entries(fullAnalysis.keyword_analysis).slice(0, 15).map(([keyword, count]) => (
                        <span key={keyword} className="px-2 py-1 bg-white border border-gray-300 rounded text-xs">
                          {keyword} <span className="font-bold text-blue-600">×{count.count}</span>
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* Modal Footer */}
            <div className="sticky bottom-0 bg-gray-50 border-t border-gray-200 px-6 py-4">
              <button
                onClick={() => setShowModal(false)}
                className="w-full px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors font-medium"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  )
}
