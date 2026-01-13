# 🚀 Complete Setup Guide

## Step-by-Step Instructions to Get Your AI Job Matcher Running

---

## ✅ Step 1: Install Prerequisites

### 1.1 Install Python 3.9+
- Download from: https://www.python.org/downloads/
- During installation, check "Add Python to PATH"
- Verify: `python --version`

### 1.2 Install Node.js 18+
- Download from: https://nodejs.org/
- Install LTS version
- Verify: `node --version` and `npm --version`

### 1.3 Install PostgreSQL 14+
- Download from: https://www.postgresql.org/download/
- Remember your postgres password!
- Verify: `psql --version`

---

## ✅ Step 2: Set Up Database

### 2.1 Create Database
Open terminal/PowerShell and run:

```bash
# Connect to PostgreSQL
psql -U postgres

# Create database (inside psql)
CREATE DATABASE job_matcher;

# Exit psql
\q
```

Alternative using pgAdmin:
1. Open pgAdmin
2. Right-click "Databases" > "Create" > "Database"
3. Name it: `job_matcher`

---

## ✅ Step 3: Backend Setup

### 3.1 Navigate to Backend Directory
```bash
cd d:\projects\proj_interview\backend
```

### 3.2 Create Virtual Environment (Recommended)
```bash
# Create virtual environment
python -m venv venv

# Activate it (Windows)
venv\Scripts\activate

# Activate it (Mac/Linux)
source venv/bin/activate
```

### 3.3 Install Python Dependencies
```bash
pip install -r requirements.txt
```

This will install:
- FastAPI, Uvicorn (Web framework)
- SQLAlchemy, psycopg2 (Database)
- pdfplumber (PDF parsing)
- spaCy, sentence-transformers (AI/NLP)
- And more...

**Note**: This may take 5-10 minutes depending on your internet speed.

### 3.4 Download spaCy Language Model
```bash
python -m spacy download en_core_web_sm
```

### 3.5 Configure Environment
```bash
# Copy example env file
cp .env.example .env

# Edit .env file with your database credentials
```

Edit `.env` file:
```ini
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/job_matcher
```

Replace `YOUR_PASSWORD` with your PostgreSQL password.

### 3.6 Initialize Database
```bash
python init_db.py
```

This will:
- Create all database tables
- Load 15 sample job postings
- Generate embeddings for all jobs

### 3.7 Start Backend Server
```bash
python main.py
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

**🎉 Backend is now running!**

Visit http://localhost:8000/docs to see API documentation.

---

## ✅ Step 4: Frontend Setup

### 4.1 Open New Terminal
Keep the backend terminal running and open a new one.

### 4.2 Navigate to Frontend Directory
```bash
cd d:\projects\proj_interview\frontend
```

### 4.3 Install Node Dependencies
```bash
npm install
```

This installs:
- Next.js, React (Frontend framework)
- Tailwind CSS (Styling)
- Axios (HTTP client)
- TypeScript (Type safety)

**Note**: This may take 3-5 minutes.

### 4.4 Configure Environment
```bash
# Copy example env file
cp .env.local.example .env.local
```

The default configuration should work:
```ini
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 4.5 Start Development Server
```bash
npm run dev
```

You should see:
```
ready - started server on 0.0.0.0:3000, url: http://localhost:3000
```

**🎉 Frontend is now running!**

---

## ✅ Step 5: Test the Application

### 5.1 Open Browser
Navigate to: http://localhost:3000

### 5.2 Prepare a Resume
You need a PDF resume to test with. If you don't have one:
- Create a simple resume in Word/Google Docs
- Include: your skills, education, experience
- Export as PDF

### 5.3 Upload Resume
1. Click "Upload a file" or drag & drop your PDF
2. Click "Analyze Resume & Find Matches"
3. Wait for analysis (10-30 seconds)

### 5.4 View Results
You should see:
- Top job matches ranked by relevance
- Match scores (0-100%)
- Matching skills
- Missing skills
- Detailed explanations

### 5.5 Explore Job Details
Click "Show Details" on any job card to see:
- Full job description
- Why it matches
- Skill breakdown
- Areas to improve

---

## ✅ Step 6: Verify Everything Works

### Backend Health Check
```bash
curl http://localhost:8000/health
```

Should return: `{"status":"healthy"}`

### List Jobs
```bash
curl http://localhost:8000/jobs/
```

Should return array of job postings.

### API Documentation
Visit: http://localhost:8000/docs

You should see interactive API documentation.

---

## 🐛 Troubleshooting

### Issue: "psycopg2 installation failed"
**Solution**: 
```bash
pip install psycopg2-binary
```

### Issue: "Can't connect to database"
**Solutions**:
1. Verify PostgreSQL is running
2. Check database credentials in `.env`
3. Ensure database `job_matcher` exists
4. Try: `psql -U postgres -d job_matcher` to test connection

### Issue: "ModuleNotFoundError: No module named 'app'"
**Solution**:
- Ensure you're in the backend directory
- Virtual environment is activated
- Run: `pip install -r requirements.txt` again

### Issue: "Port 8000 already in use"
**Solution**:
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Mac/Linux
lsof -ti:8000 | xargs kill -9
```

### Issue: "npm install fails"
**Solution**:
1. Delete `node_modules` and `package-lock.json`
2. Run `npm install` again
3. Or try: `npm install --legacy-peer-deps`

### Issue: "Frontend can't connect to backend"
**Solutions**:
1. Verify backend is running (http://localhost:8000)
2. Check CORS settings in backend
3. Verify `.env.local` has correct API URL

### Issue: "Sentence transformers download is slow"
**Note**: First run downloads ~100MB model. This is normal.
- Be patient, it only happens once
- Model is cached for future use

---

## 📝 Daily Development Workflow

### Starting the Application

1. **Terminal 1 - Backend**:
```bash
cd d:\projects\proj_interview\backend
venv\Scripts\activate  # Windows
python main.py
```

2. **Terminal 2 - Frontend**:
```bash
cd d:\projects\proj_interview\frontend
npm run dev
```

3. Open browser: http://localhost:3000

### Stopping the Application

- Press `Ctrl+C` in both terminals
- Or close the terminal windows

---

## 🎯 Next Steps

### Add More Jobs
```bash
# Edit data/sample_jobs.json
# Then run:
cd backend
python init_db.py
```

### Customize Frontend
- Edit colors in `frontend/tailwind.config.js`
- Modify components in `frontend/components/`
- Update styles in `frontend/app/globals.css`

### Improve Resume Parsing
- Edit `backend/app/services/resume_parser.py`
- Add more skill keywords
- Enhance education/experience extraction

### Deploy to Production
See deployment guides in:
- `backend/README.md` - Backend deployment
- `frontend/README.md` - Frontend deployment
- Main `README.md` - Full deployment guide

---

## 📚 Learning Resources

### FastAPI
- Docs: https://fastapi.tiangolo.com/
- Tutorial: Build REST APIs

### Next.js
- Docs: https://nextjs.org/docs
- Tutorial: React framework

### Sentence Transformers
- Docs: https://www.sbert.net/
- Tutorial: Generate embeddings

### PostgreSQL
- Docs: https://www.postgresql.org/docs/
- Tutorial: SQL basics

---

## ✅ You're All Set!

Your AI Job Matcher is now running locally. You have:

✅ Backend API with AI matching
✅ Frontend with modern UI
✅ PostgreSQL database
✅ Sample jobs loaded
✅ Resume upload working
✅ Semantic matching enabled
✅ Explainable AI results

**Start building and experimenting! 🚀**

Questions? Check the README.md files in each directory.
