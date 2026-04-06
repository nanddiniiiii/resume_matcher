export interface Resume {
  id: number
  filename: string
  skills: string[]
  education: any[]
  experience: any[]
  created_at: string
}

export interface ResumeUploadResponse {
  id: number
  filename: string
  message: string
  skills_found: string[]
  education_found: number
  experience_found: number
}

export interface Job {
  id: number
  title: string
  company: string
  description: string
  required_skills: string[]
  location: string
  job_type: string
  created_at: string
  source?: string | null
  source_url?: string | null
  source_job_id?: string | null
  scraped_at?: string | null
  expires_at?: string | null
  is_active?: boolean
}

export interface JobMatchExplanation {
  match_quality: string
  overall_score: number
  skill_match_percentage: number
  recommendation: string
  skill_analysis: string
  strengths: string[]
  areas_to_improve: string[]
  why_this_matches: string
}

export interface JobMatch {
  job: Job
  similarity_score: number
  matching_skills: string[]
  missing_skills: string[]
  explanation: JobMatchExplanation
}

export interface JobMatchListResponse {
  total_matches: number
  matches: JobMatch[]
}
