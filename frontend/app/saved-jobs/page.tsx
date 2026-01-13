"use client";

import { useState, useEffect } from "react";
import { useAuth } from "@/contexts/AuthContext";
import { useTheme } from "@/contexts/ThemeContext";
import Header from "@/components/Header";
import { toast } from "react-hot-toast";

interface SavedJob {
  saved_job_id: number;
  saved_at: string;
  notes: string | null;
  job: {
    id: number;
    title: string;
    company: string;
    location: string;
    job_type: string;
    skills_required: string[];
    description: string;
  };
}

export default function SavedJobsPage() {
  const { token } = useAuth();
  const { isDarkMode } = useTheme();
  const [savedJobs, setSavedJobs] = useState<SavedJob[]>([]);
  const [loading, setLoading] = useState(true);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const limit = 10;

  useEffect(() => {
    if (token) {
      fetchSavedJobs();
    }
  }, [token, page]);

  const fetchSavedJobs = async () => {
    try {
      setLoading(true);
      const skip = (page - 1) * limit;
      const response = await fetch(
        `http://localhost:8000/api/jobs/saved?skip=${skip}&limit=${limit}`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      if (response.ok) {
        const data = await response.json();
        setSavedJobs(data.saved_jobs);
        setTotal(data.total);
      }
    } catch (error) {
      toast.error("Failed to load saved jobs");
    } finally {
      setLoading(false);
    }
  };

  const handleUnsave = async (jobId: number) => {
    try {
      const response = await fetch(
        `http://localhost:8000/api/jobs/${jobId}/save`,
        {
          method: "DELETE",
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      if (response.ok) {
        toast.success("Job removed from saved list");
        fetchSavedJobs();
      }
    } catch (error) {
      toast.error("Failed to remove job");
    }
  };

  const handleApply = async (jobId: number) => {
    try {
      const response = await fetch(
        "http://localhost:8000/api/applications/",
        {
          method: "POST",
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ job_id: jobId }),
        }
      );

      if (response.ok) {
        toast.success("Application tracked!");
      } else {
        const data = await response.json();
        toast.error(data.detail || "Failed to track application");
      }
    } catch (error) {
      toast.error("Failed to track application");
    }
  };

  const totalPages = Math.ceil(total / limit);

  return (
    <div className={isDarkMode ? "dark" : ""}>
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800">
        <Header />

        <main className="container mx-auto px-4 py-12">
          <div className="max-w-6xl mx-auto">
            <div className="flex items-center justify-between mb-8">
              <div>
                <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-2">
                  Saved Jobs
                </h1>
                <p className="text-gray-600 dark:text-gray-400">
                  {total} jobs saved for later
                </p>
              </div>
            </div>

            {loading ? (
              <div className="text-center py-12">
                <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
              </div>
            ) : savedJobs.length === 0 ? (
              <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-12 text-center">
                <svg
                  className="mx-auto h-16 w-16 text-gray-400 mb-4"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z"
                  />
                </svg>
                <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
                  No saved jobs yet
                </h3>
                <p className="text-gray-600 dark:text-gray-400">
                  Start saving jobs you're interested in to view them here
                </p>
              </div>
            ) : (
              <div className="space-y-6">
                {savedJobs.map((savedJob) => (
                  <div
                    key={savedJob.saved_job_id}
                    className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 hover:shadow-xl transition-shadow"
                  >
                    <div className="flex justify-between items-start mb-4">
                      <div className="flex-1">
                        <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
                          {savedJob.job.title}
                        </h2>
                        <div className="flex items-center gap-4 text-gray-600 dark:text-gray-400 mb-2">
                          <span className="flex items-center gap-1">
                            <svg
                              className="w-5 h-5"
                              fill="none"
                              viewBox="0 0 24 24"
                              stroke="currentColor"
                            >
                              <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                strokeWidth={2}
                                d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"
                              />
                            </svg>
                            {savedJob.job.company}
                          </span>
                          <span className="flex items-center gap-1">
                            <svg
                              className="w-5 h-5"
                              fill="none"
                              viewBox="0 0 24 24"
                              stroke="currentColor"
                            >
                              <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                strokeWidth={2}
                                d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"
                              />
                              <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                strokeWidth={2}
                                d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"
                              />
                            </svg>
                            {savedJob.job.location}
                          </span>
                          <span className="px-3 py-1 bg-indigo-100 dark:bg-indigo-900 text-indigo-800 dark:text-indigo-200 rounded-full text-sm">
                            {savedJob.job.job_type}
                          </span>
                        </div>
                        <p className="text-gray-700 dark:text-gray-300 mb-4">
                          {savedJob.job.description}
                        </p>
                        <div className="flex flex-wrap gap-2 mb-4">
                          {savedJob.job.skills_required.map((skill, idx) => (
                            <span
                              key={idx}
                              className="px-3 py-1 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg text-sm"
                            >
                              {skill}
                            </span>
                          ))}
                        </div>
                        {savedJob.notes && (
                          <div className="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg p-3 mb-4">
                            <p className="text-sm text-yellow-800 dark:text-yellow-200">
                              <strong>Note:</strong> {savedJob.notes}
                            </p>
                          </div>
                        )}
                        <p className="text-sm text-gray-500 dark:text-gray-400">
                          Saved on{" "}
                          {new Date(savedJob.saved_at).toLocaleDateString()}
                        </p>
                      </div>
                    </div>

                    <div className="flex gap-3">
                      <button
                        onClick={() => handleApply(savedJob.job.id)}
                        className="flex-1 bg-indigo-600 hover:bg-indigo-700 text-white py-2 px-4 rounded-lg transition-colors font-medium"
                      >
                        Track Application
                      </button>
                      <button
                        onClick={() => handleUnsave(savedJob.job.id)}
                        className="px-4 py-2 border border-red-300 dark:border-red-700 text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg transition-colors font-medium"
                      >
                        Remove
                      </button>
                    </div>
                  </div>
                ))}

                {/* Pagination */}
                {totalPages > 1 && (
                  <div className="flex justify-center gap-2 mt-8">
                    <button
                      onClick={() => setPage((p) => Math.max(1, p - 1))}
                      disabled={page === 1}
                      className="px-4 py-2 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
                    >
                      Previous
                    </button>
                    <span className="px-4 py-2 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg">
                      Page {page} of {totalPages}
                    </span>
                    <button
                      onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                      disabled={page === totalPages}
                      className="px-4 py-2 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
                    >
                      Next
                    </button>
                  </div>
                )}
              </div>
            )}
          </div>
        </main>
      </div>
    </div>
  );
}
