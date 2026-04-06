# AI Job Matcher

Full-stack application for resume-based job discovery using semantic matching, explainable recommendations, and job-tracking workflows.

## What This Project Does

- Uploads and parses PDF resumes.
- Generates resume/job embeddings for semantic similarity matching.
- Returns ranked matches with matching skills, missing skills, and explanations.
- Supports user authentication (JWT), saved jobs, and application tracking.
- Includes job search and admin scraping endpoints for refreshing listings.
- Provides resume optimization tips against a selected job (ATS-style analysis).

## Stack

- Frontend: Next.js 14, React 18, TypeScript, Tailwind CSS
- Backend: FastAPI, SQLAlchemy, Pydantic
- Database: PostgreSQL
- AI/NLP: sentence-transformers, scikit-learn, spaCy, pdfplumber
- Scraping: requests, beautifulsoup4, aiohttp

## Implemented Feature Areas

### Candidate Workflow

- Resume upload and parsing (`/api/resumes/upload`)
- Top-N semantic matches (`/api/matches/{resume_id}`)
- Match explanations (score, matching skills, missing skills)
- Saved jobs (`/api/jobs/{job_id}/save`, `/api/jobs/saved`)
- Application tracking (`/api/applications`)
- Account stats and activity (`/api/users/stats`)

### Job Data Workflow

- CRUD + search endpoints for jobs (`/api/jobs`, `/api/jobs/search`)
- Background scraping trigger (`/api/scraper/run`)
- Scraper status and expiration management (`/api/scraper/status`, `/api/scraper/mark-expired`)

### Resume Optimization Workflow

- Resume-vs-job analyzer (`/api/resume-analyzer/analyze`)
- Quick tips endpoint (`/api/resume-analyzer/quick-tips/{job_id}`)

## Architecture

```text
Frontend (Next.js)
         |
         v
Backend API (FastAPI)
         |
         +--> Auth + User features
         +--> Resume parsing + Matching services
         +--> Job search + Scraping services
         |
         v
PostgreSQL (users, resumes, jobs, matches, saved_jobs, applications)
```

## Repository Layout

```text
proj_interview/
        backend/
                app/
                        api/
                        models/
                        services/
                        auth.py
                        config.py
                        database.py
                main.py
                init_db.py
                requirements.txt
        frontend/
                app/
                components/
                contexts/
                lib/
                package.json
```

## Local Setup

### 1. Backend

```powershell
cd backend
pip install -r requirements.txt
python -m spacy download en_core_web_sm
python init_db.py
python main.py
```

Backend runs at http://localhost:8000
Swagger docs: http://localhost:8000/docs

### 2. Frontend

```powershell
cd frontend
npm install
npm run dev
```

Frontend runs at http://localhost:3000

## Configuration Notes

- Backend defaults are in `backend/app/config.py`.
- Frontend includes `NEXT_PUBLIC_API_URL` support.
- Some frontend pages currently call `http://localhost:8000` directly, so local backend on port 8000 is expected unless those calls are refactored.

## API Summary

- Auth: `/api/auth/register`, `/api/auth/login`, `/api/auth/login/json`, `/api/auth/me`
- Resumes: `/api/resumes/upload`, `/api/resumes`, `/api/resumes/{id}`
- Matches: `/api/matches/{resume_id}`, `/api/matches/history/{resume_id}`
- Jobs: `/api/jobs`, `/api/jobs/search`, `/api/jobs/{id}`
- Saved jobs: `/api/jobs/{job_id}/save`, `/api/jobs/saved`
- Applications: `/api/applications`
- User stats: `/api/users/stats`
- Scraper: `/api/scraper/run`, `/api/scraper/status`, `/api/scraper/mark-expired`, `/api/scraper/sources`
- Resume analyzer: `/api/resume-analyzer/analyze`, `/api/resume-analyzer/quick-tips/{job_id}`


- Built an end-to-end AI job matching product with Next.js + FastAPI + PostgreSQL.
- Implemented semantic ranking using sentence embeddings and cosine similarity.
- Added explainable matching output with skill overlap and gap insights.
- Developed authenticated user workflows: saved jobs, application tracking, and profile stats.
- Extended the platform with job scraping and resume optimization analysis endpoints.

