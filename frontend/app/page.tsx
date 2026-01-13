'use client'

import { useState } from 'react'
import ResumeUpload from '@/components/ResumeUpload'
import JobMatches from '@/components/JobMatches'

export default function Home() {
  const [resumeId, setResumeId] = useState<number | null>(null)
  const [showMatches, setShowMatches] = useState(false)

  const handleUploadSuccess = (id: number) => {
    setResumeId(id)
    setShowMatches(true)
  }

  const handleBackToUpload = () => {
    setShowMatches(false)
    setResumeId(null)
  }

  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                🎯 AI Job Matcher
              </h1>
              <p className="text-sm text-gray-600 mt-1">
                Find your perfect role with AI-powered matching
              </p>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {!showMatches ? (
          <>
            {/* Hero Section */}
            <div className="text-center mb-12">
              <h2 className="text-4xl font-extrabold text-gray-900 sm:text-5xl mb-4">
                Upload Your Resume
              </h2>
              <p className="text-xl text-gray-600 max-w-3xl mx-auto">
                Our AI will analyze your skills and experience to recommend the best matching jobs.
                Get detailed explanations for every recommendation.
              </p>
            </div>

            {/* Features */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
              <div className="bg-white p-6 rounded-lg shadow-md border border-gray-100">
                <div className="text-3xl mb-3">🧠</div>
                <h3 className="text-lg font-semibold mb-2">Semantic Matching</h3>
                <p className="text-gray-600 text-sm">
                  Advanced AI analyzes your resume beyond simple keywords
                </p>
              </div>
              <div className="bg-white p-6 rounded-lg shadow-md border border-gray-100">
                <div className="text-3xl mb-3">💡</div>
                <h3 className="text-lg font-semibold mb-2">Explainable AI</h3>
                <p className="text-gray-600 text-sm">
                  Understand exactly why each job matches your profile
                </p>
              </div>
              <div className="bg-white p-6 rounded-lg shadow-md border border-gray-100">
                <div className="text-3xl mb-3">📊</div>
                <h3 className="text-lg font-semibold mb-2">Skill Gap Analysis</h3>
                <p className="text-gray-600 text-sm">
                  See what skills you have and what you need to develop
                </p>
              </div>
            </div>

            {/* Upload Component */}
            <ResumeUpload onUploadSuccess={handleUploadSuccess} />
          </>
        ) : (
          <>
            {/* Back Button */}
            <button
              onClick={handleBackToUpload}
              className="mb-6 flex items-center text-primary-600 hover:text-primary-700 font-medium"
            >
              <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
              Upload New Resume
            </button>

            {/* Job Matches */}
            {resumeId && <JobMatches resumeId={resumeId} />}
          </>
        )}
      </div>

      {/* Footer */}
      <footer className="bg-white border-t mt-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <p className="text-center text-gray-500 text-sm">
            Built with Next.js, FastAPI, and AI • Semantic job matching using embeddings
          </p>
        </div>
      </footer>
    </main>
  )
}
