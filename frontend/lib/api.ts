import axios from 'axios'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Resume API
export const resumeAPI = {
  upload: async (file: File, userEmail: string = 'demo@example.com') => {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('user_email', userEmail)

    const response = await api.post('/api/resumes/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return response.data
  },

  getResume: async (resumeId: number) => {
    const response = await api.get(`/api/resumes/${resumeId}`)
    return response.data
  },

  listResumes: async (userEmail: string = 'demo@example.com') => {
    const response = await api.get(`/api/resumes/`, {
      params: { user_email: userEmail },
    })
    return response.data
  },

  deleteResume: async (resumeId: number) => {
    const response = await api.delete(`/api/resumes/${resumeId}`)
    return response.data
  },
}

// Job API
export const jobAPI = {
  listJobs: async (jobType?: string) => {
    const response = await api.get('/api/jobs/', {
      params: { job_type: jobType },
    })
    return response.data
  },

  getJob: async (jobId: number) => {
    const response = await api.get(`/api/jobs/${jobId}`)
    return response.data
  },
}

// Job Matching API
export const matchAPI = {
  getMatches: async (resumeId: number, topN: number = 10) => {
    const response = await api.get(`/api/matches/${resumeId}`, {
      params: { top_n: topN },
    })
    return response.data
  },

  getMatchHistory: async (resumeId: number) => {
    const response = await api.get(`/api/matches/history/${resumeId}`)
    return response.data
  },
}

export default api
