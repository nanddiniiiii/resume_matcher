import axios from 'axios'
import Cookies from 'js-cookie'
import { API_BASE_URL } from './config'



const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

api.interceptors.request.use((config) => {
  const token = Cookies.get('access_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

// Resume API
export const resumeAPI = {
  upload: async (file: File) => {
    const formData = new FormData()
    formData.append('file', file)

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

  listResumes: async () => {
    const response = await api.get('/api/resumes/')
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
