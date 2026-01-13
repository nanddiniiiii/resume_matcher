"use client";

import { useState, useEffect } from "react";
import { useAuth } from "@/contexts/AuthContext";
import { useTheme } from "@/contexts/ThemeContext";
import Header from "@/components/Header";
import { toast } from "react-hot-toast";

interface Application {
  application_id: number;
  status: string;
  applied_date: string;
  notes: string | null;
  job: {
    id: number;
    title: string;
    company: string;
    location: string;
    job_type: string;
  };
}

const statusColors = {
  applied: "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200",
  interviewing: "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200",
  accepted: "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200",
  rejected: "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200",
};

export default function ApplicationsPage() {
  const { token } = useAuth();
  const { isDarkMode } = useTheme();
  const [applications, setApplications] = useState<Application[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<string>("");
  const [editingId, setEditingId] = useState<number | null>(null);
  const [newStatus, setNewStatus] = useState("");
  const [total, setTotal] = useState(0);

  useEffect(() => {
    if (token) {
      fetchApplications();
    }
  }, [token, filter]);

  const fetchApplications = async () => {
    try {
      setLoading(true);
      const url = filter
        ? `http://localhost:8000/api/applications/?status=${filter}`
        : "http://localhost:8000/api/applications/";

      const response = await fetch(url, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setApplications(data.applications);
        setTotal(data.total);
      }
    } catch (error) {
      toast.error("Failed to load applications");
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateStatus = async (appId: number, status: string) => {
    try {
      const response = await fetch(
        `http://localhost:8000/api/applications/${appId}`,
        {
          method: "PUT",
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ status }),
        }
      );

      if (response.ok) {
        toast.success("Status updated!");
        setEditingId(null);
        fetchApplications();
      }
    } catch (error) {
      toast.error("Failed to update status");
    }
  };

  const handleDelete = async (appId: number) => {
    if (!confirm("Are you sure you want to delete this application?")) return;

    try {
      const response = await fetch(
        `http://localhost:8000/api/applications/${appId}`,
        {
          method: "DELETE",
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      if (response.ok) {
        toast.success("Application deleted");
        fetchApplications();
      }
    } catch (error) {
      toast.error("Failed to delete application");
    }
  };

  const stats = {
    applied: applications.filter((a) => a.status === "applied").length,
    interviewing: applications.filter((a) => a.status === "interviewing").length,
    accepted: applications.filter((a) => a.status === "accepted").length,
    rejected: applications.filter((a) => a.status === "rejected").length,
  };

  return (
    <div className={isDarkMode ? "dark" : ""}>
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800">
        <Header />

        <main className="container mx-auto px-4 py-12">
          <div className="max-w-6xl mx-auto">
            <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-8">
              Application Tracker
            </h1>

            {/* Stats Cards */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
              <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
                <div className="text-3xl font-bold text-blue-600 mb-1">
                  {stats.applied}
                </div>
                <div className="text-gray-600 dark:text-gray-400">Applied</div>
              </div>
              <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
                <div className="text-3xl font-bold text-yellow-600 mb-1">
                  {stats.interviewing}
                </div>
                <div className="text-gray-600 dark:text-gray-400">
                  Interviewing
                </div>
              </div>
              <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
                <div className="text-3xl font-bold text-green-600 mb-1">
                  {stats.accepted}
                </div>
                <div className="text-gray-600 dark:text-gray-400">Accepted</div>
              </div>
              <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
                <div className="text-3xl font-bold text-red-600 mb-1">
                  {stats.rejected}
                </div>
                <div className="text-gray-600 dark:text-gray-400">Rejected</div>
              </div>
            </div>

            {/* Filter */}
            <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-4 mb-6">
              <div className="flex gap-2">
                <button
                  onClick={() => setFilter("")}
                  className={`px-4 py-2 rounded-lg transition-colors ${
                    filter === ""
                      ? "bg-indigo-600 text-white"
                      : "bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300"
                  }`}
                >
                  All ({total})
                </button>
                <button
                  onClick={() => setFilter("applied")}
                  className={`px-4 py-2 rounded-lg transition-colors ${
                    filter === "applied"
                      ? "bg-blue-600 text-white"
                      : "bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300"
                  }`}
                >
                  Applied
                </button>
                <button
                  onClick={() => setFilter("interviewing")}
                  className={`px-4 py-2 rounded-lg transition-colors ${
                    filter === "interviewing"
                      ? "bg-yellow-600 text-white"
                      : "bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300"
                  }`}
                >
                  Interviewing
                </button>
                <button
                  onClick={() => setFilter("accepted")}
                  className={`px-4 py-2 rounded-lg transition-colors ${
                    filter === "accepted"
                      ? "bg-green-600 text-white"
                      : "bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300"
                  }`}
                >
                  Accepted
                </button>
                <button
                  onClick={() => setFilter("rejected")}
                  className={`px-4 py-2 rounded-lg transition-colors ${
                    filter === "rejected"
                      ? "bg-red-600 text-white"
                      : "bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300"
                  }`}
                >
                  Rejected
                </button>
              </div>
            </div>

            {loading ? (
              <div className="text-center py-12">
                <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
              </div>
            ) : applications.length === 0 ? (
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
                    d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                  />
                </svg>
                <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
                  No applications yet
                </h3>
                <p className="text-gray-600 dark:text-gray-400">
                  Start tracking your job applications here
                </p>
              </div>
            ) : (
              <div className="space-y-4">
                {applications.map((app) => (
                  <div
                    key={app.application_id}
                    className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 hover:shadow-xl transition-shadow"
                  >
                    <div className="flex justify-between items-start mb-4">
                      <div className="flex-1">
                        <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-2">
                          {app.job.title}
                        </h3>
                        <div className="flex items-center gap-4 text-gray-600 dark:text-gray-400 mb-2">
                          <span>{app.job.company}</span>
                          <span>•</span>
                          <span>{app.job.location}</span>
                          <span>•</span>
                          <span className="capitalize">{app.job.job_type}</span>
                        </div>
                        <p className="text-sm text-gray-500 dark:text-gray-400">
                          Applied on{" "}
                          {new Date(app.applied_date).toLocaleDateString()}
                        </p>
                      </div>

                      {editingId === app.application_id ? (
                        <div className="flex gap-2">
                          <select
                            value={newStatus}
                            onChange={(e) => setNewStatus(e.target.value)}
                            className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                          >
                            <option value="applied">Applied</option>
                            <option value="interviewing">Interviewing</option>
                            <option value="accepted">Accepted</option>
                            <option value="rejected">Rejected</option>
                          </select>
                          <button
                            onClick={() =>
                              handleUpdateStatus(app.application_id, newStatus)
                            }
                            className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
                          >
                            Save
                          </button>
                          <button
                            onClick={() => setEditingId(null)}
                            className="px-4 py-2 bg-gray-300 dark:bg-gray-600 text-gray-700 dark:text-gray-200 rounded-lg hover:bg-gray-400 dark:hover:bg-gray-500"
                          >
                            Cancel
                          </button>
                        </div>
                      ) : (
                        <div className="flex gap-2 items-center">
                          <span
                            className={`px-4 py-2 rounded-lg font-medium capitalize ${
                              statusColors[app.status as keyof typeof statusColors]
                            }`}
                          >
                            {app.status}
                          </span>
                          <button
                            onClick={() => {
                              setEditingId(app.application_id);
                              setNewStatus(app.status);
                            }}
                            className="px-3 py-2 text-indigo-600 dark:text-indigo-400 hover:bg-indigo-50 dark:hover:bg-indigo-900/20 rounded-lg"
                          >
                            Edit
                          </button>
                          <button
                            onClick={() => handleDelete(app.application_id)}
                            className="px-3 py-2 text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg"
                          >
                            Delete
                          </button>
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </main>
      </div>
    </div>
  );
}
