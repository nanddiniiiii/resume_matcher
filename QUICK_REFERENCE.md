> Historical notes. See [README.md](README.md) for current setup and behavior, and [docs/AUDIT.md](docs/AUDIT.md) for verified fixes and limitations.

# ⚡ Quick Reference Card

One-page reference for common commands and workflows.

---

## 🚀 Quick Start Commands

### Start Backend
```bash
cd backend
venv\Scripts\activate    # Windows
source venv/bin/activate # Mac/Linux
python main.py
```
**URL**: http://localhost:8000
**Docs**: http://localhost:8000/docs

### Start Frontend
```bash
cd frontend
npm run dev
```
**URL**: http://localhost:3000

---

## 📦 Installation Commands

### Backend
```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm
cp .env.example .env
python init_db.py
```

### Frontend
```bash
cd frontend
npm install
cp .env.local.example .env.local
```

---

## 🗄️ Database Commands

### Create Database
```bash
psql -U postgres -c "CREATE DATABASE job_matcher;"
```

### Connect to Database
```bash
psql -U postgres -d job_matcher
```

### Useful SQL Commands
```sql
-- List all tables
\dt

-- Count jobs
SELECT COUNT(*) FROM jobs;

-- View resumes
SELECT id, filename, array_length(skills, 1) as skill_count FROM resumes;

-- Check embeddings
SELECT COUNT(*) FROM jobs WHERE embedding IS NOT NULL;

-- Exit
\q
```

### Reset Database
```bash
psql -U postgres -c "DROP DATABASE job_matcher;"
psql -U postgres -c "CREATE DATABASE job_matcher;"
cd backend
python init_db.py
```

---

## 🔧 Troubleshooting Commands

### Check if Ports are in Use
```bash
# Windows
netstat -ano | findstr :8000
netstat -ano | findstr :3000

# Mac/Linux
lsof -ti:8000
lsof -ti:3000
```

### Kill Process on Port
```bash
# Windows
taskkill /PID <PID> /F

# Mac/Linux
kill -9 <PID>
```

### Check Services Running
```bash
# PostgreSQL (Windows)
Get-Service -Name postgresql*

# PostgreSQL (Mac)
brew services list
```

### View Logs
```bash
# Backend - in terminal where it's running
# Frontend - browser console (F12)
```

---

## 🧪 Testing Commands

### Test Backend API
```bash
# Health check
curl http://localhost:8000/health

# List jobs
curl http://localhost:8000/jobs/

# Upload resume (replace path)
curl -X POST "http://localhost:8000/resumes/upload" \
  -F "file=@resume.pdf" \
  -F "user_email=demo@example.com"

# Get matches (replace resume_id)
curl http://localhost:8000/matches/1
```

### Test Frontend
- Open: http://localhost:3000
- Upload a PDF resume
- View matches

---

## 📁 Important Files

### Configuration
```
backend/.env              # Backend environment variables
frontend/.env.local       # Frontend environment variables
backend/app/config.py     # Application configuration
```

### Main Files
```
backend/main.py                          # FastAPI entry point
backend/app/api/matches.py               # Core matching logic
backend/app/services/job_matcher.py      # AI matching engine
backend/app/services/resume_parser.py    # Resume parsing
frontend/app/page.tsx                    # Frontend home page
frontend/components/JobMatches.tsx       # Matches display
```

### Data Files
```
backend/data/sample_jobs.json            # Sample jobs
backend/uploads/                         # Uploaded resumes
```

---

## 🔑 Environment Variables

### Backend (.env)
```ini
DATABASE_URL=postgresql://postgres:password@localhost:5432/job_matcher
DEBUG=True
API_PORT=8000
CORS_ORIGINS=http://localhost:3000
```

### Frontend (.env.local)
```ini
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## 📊 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/resumes/upload` | Upload resume |
| GET | `/resumes/{id}` | Get resume details |
| GET | `/resumes/` | List all resumes |
| DELETE | `/resumes/{id}` | Delete resume |
| POST | `/jobs/` | Create job |
| GET | `/jobs/` | List jobs |
| GET | `/jobs/{id}` | Get job details |
| GET | `/matches/{resume_id}` | **Get job matches** |
| GET | `/matches/history/{resume_id}` | Get match history |

---

## 🏗️ Project Structure

```
proj_interview/
├── backend/              # Python FastAPI
│   ├── app/
│   │   ├── api/         # REST endpoints
│   │   ├── models/      # Database models
│   │   └── services/    # Business logic
│   ├── data/            # Sample data
│   ├── uploads/         # Uploaded files
│   └── main.py          # Entry point
│
├── frontend/            # Next.js React
│   ├── app/            # Pages
│   ├── components/     # React components
│   └── lib/            # Utilities
│
├── README.md           # Main docs
├── SETUP_GUIDE.md      # Setup instructions
└── PROJECT_SUMMARY.md  # Project overview
```

---

## 🎯 Common Workflows

### Add New Job
```bash
# Option 1: Edit sample_jobs.json and re-run init_db.py

# Option 2: Use API
curl -X POST http://localhost:8000/jobs/ \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Software Engineer",
    "company": "Tech Corp",
    "description": "Job description",
    "required_skills": ["python", "sql"],
    "location": "Remote",
    "job_type": "full-time"
  }'
```

### Debug Resume Parsing
```python
# In Python shell
from app.services.resume_parser import ResumeParser
parser = ResumeParser()
data = parser.parse_resume('path/to/resume.pdf')
print(data['skills'])
```

### Check Match Scores
```bash
# Get detailed match results
curl http://localhost:8000/matches/1?top_n=10 | python -m json.tool
```

---

## 💡 Development Tips

### Hot Reload
Both backend and frontend support hot reload:
- **Backend**: Changes auto-reload when `DEBUG=True`
- **Frontend**: Changes auto-reload automatically

### Debugging
```python
# Add print statements in backend
print(f"Debug: {variable}")

# Use browser console for frontend
console.log(data)
```

### Performance
- First resume upload is slow (model download)
- Subsequent uploads are fast
- Matching is instant for < 100 jobs

---

## 🚢 Deployment Quick Reference

### Vercel (Frontend)
```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
cd frontend
vercel
```

### Render (Backend)
1. Push code to GitHub
2. Create new Web Service on Render
3. Set environment variables
4. Deploy

---

## 📚 Key Concepts

### Embeddings
- Text → 384-dimensional vector
- Captures semantic meaning
- Enables similarity comparison

### Cosine Similarity
- Measures angle between vectors
- Range: 0 (different) to 1 (identical)
- Used for ranking jobs

### Skills Extraction
- Keyword matching
- Expandable skill list
- Case-insensitive

---

## ⚙️ Useful Git Commands

```bash
# Initialize repo
git init
git add .
git commit -m "Initial commit"

# Create GitHub repo, then:
git remote add origin <your-repo-url>
git push -u origin main
```

---

## 🆘 Emergency Commands

### Complete Reset
```bash
# Backend
cd backend
rm -rf venv __pycache__
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# Frontend
cd frontend
rm -rf node_modules .next
npm install

# Database
psql -U postgres -c "DROP DATABASE job_matcher;"
psql -U postgres -c "CREATE DATABASE job_matcher;"
python init_db.py
```

---

## 📞 Quick Help

**Backend won't start?**
→ Check .env, activate venv, verify PostgreSQL

**Frontend won't start?**
→ Run npm install, delete .next folder

**No matches found?**
→ Verify jobs exist, check resume parsing

**Slow performance?**
→ Normal for first run (model download)

---

## ✅ Pre-Demo Checklist

- [ ] PostgreSQL running
- [ ] Backend running (http://localhost:8000)
- [ ] Frontend running (http://localhost:3000)
- [ ] Sample jobs loaded (check /jobs/)
- [ ] Test resume ready
- [ ] Browser dev tools closed (for clean demo)

---

## 🎤 Interview Quick Facts

- **Tech Stack**: Next.js, FastAPI, PostgreSQL
- **AI Model**: all-MiniLM-L6-v2 (sentence-transformers)
- **Matching**: Cosine similarity on embeddings
- **Database**: 4 tables (users, resumes, jobs, matches)
- **Features**: Resume parsing, semantic matching, explainable AI
- **Lines of Code**: ~3,500+

---

**Print this card and keep it handy while developing!** 📋
