# AI Job Matcher - Backend

AI-powered job recommendation platform using semantic matching.

## Setup Instructions

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 2. Download spaCy Model

```bash
python -m spacy download en_core_web_sm
```

### 3. Set Up PostgreSQL Database

Install PostgreSQL and create a database:

```sql
CREATE DATABASE job_matcher;
```

### 4. Configure Environment Variables

Copy `.env.example` to `.env` and update with your database credentials:

```bash
cp .env.example .env
```

Edit `.env`:
```
DATABASE_URL=postgresql://your_username:your_password@localhost:5432/job_matcher
```

### 5. Initialize Database

Run the initialization script to create tables and load sample jobs:

```bash
python init_db.py
```

### 6. Start the Server

```bash
python main.py
```

Or with uvicorn:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

## API Documentation

Once the server is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## API Endpoints

### Resume Management
- `POST /resumes/upload` - Upload and parse resume PDF
- `GET /resumes/{resume_id}` - Get resume details
- `GET /resumes/` - List all resumes
- `DELETE /resumes/{resume_id}` - Delete resume

### Job Management
- `POST /jobs/` - Create job posting
- `GET /jobs/` - List all jobs
- `GET /jobs/{job_id}` - Get job details
- `PUT /jobs/{job_id}` - Update job
- `DELETE /jobs/{job_id}` - Delete job

### Job Matching (Core Feature)
- `GET /matches/{resume_id}` - Get AI-powered job recommendations
- `GET /matches/history/{resume_id}` - Get match history

## Testing the API

### 1. Upload a Resume

```bash
curl -X POST "http://localhost:8000/resumes/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@your_resume.pdf" \
  -F "user_email=demo@example.com"
```

### 2. Get Job Matches

```bash
curl "http://localhost:8000/matches/1?top_n=10"
```

This will return:
- Top 10 matching jobs
- Similarity scores
- Matching skills
- Missing skills
- Detailed explanations

## Project Structure

```
backend/
├── app/
│   ├── api/              # API endpoints
│   │   ├── resumes.py    # Resume upload & management
│   │   ├── jobs.py       # Job management
│   │   ├── matches.py    # Job matching logic
│   │   └── schemas.py    # Pydantic models
│   ├── models/           # Database models
│   │   ├── user.py
│   │   ├── resume.py
│   │   ├── job.py
│   │   └── job_match.py
│   ├── services/         # Business logic
│   │   ├── resume_parser.py   # PDF parsing & NLP
│   │   └── job_matcher.py     # Semantic matching
│   ├── config.py         # Configuration
│   └── database.py       # Database connection
├── uploads/              # Uploaded resume files
├── data/                 # Sample data
│   └── sample_jobs.json
├── main.py              # FastAPI app entry point
├── init_db.py           # Database initialization
└── requirements.txt     # Python dependencies
```

## Technology Stack

- **FastAPI** - Modern Python web framework
- **SQLAlchemy** - ORM for database operations
- **PostgreSQL** - Relational database
- **pdfplumber** - PDF text extraction
- **spaCy** - NLP processing
- **Sentence Transformers** - Generate embeddings for semantic search
- **scikit-learn** - Cosine similarity calculation

## Features

✅ Resume PDF upload and parsing
✅ Skill extraction using NLP
✅ Education and experience extraction
✅ Semantic job matching using embeddings
✅ Explainable AI - shows why jobs match
✅ Skill gap analysis
✅ RESTful API with comprehensive documentation
