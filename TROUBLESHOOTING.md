# 🔧 Troubleshooting Guide

Common issues and their solutions when setting up the AI Job Matcher.

---

## 🐛 Backend Issues

### Issue: "ModuleNotFoundError: No module named 'app'"

**Cause**: Running from wrong directory or virtual environment not activated.

**Solutions**:
```bash
# 1. Make sure you're in the backend directory
cd backend

# 2. Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# 3. Verify installation
pip list | grep fastapi
```

---

### Issue: "Error: unable to open database file" or "Can't connect to database"

**Cause**: PostgreSQL not running or wrong credentials.

**Solutions**:

1. **Verify PostgreSQL is running**:
```bash
# Windows (PowerShell as Admin):
Get-Service -Name postgresql*

# If not running:
Start-Service -Name postgresql-x64-14

# Mac:
brew services list
brew services start postgresql
```

2. **Test database connection**:
```bash
psql -U postgres -d job_matcher
```

3. **Check credentials in .env**:
```ini
# backend/.env
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/job_matcher
```

4. **Verify database exists**:
```bash
psql -U postgres -c "\l" | grep job_matcher
```

5. **Create database if missing**:
```bash
psql -U postgres -c "CREATE DATABASE job_matcher;"
```

---

### Issue: "psycopg2 installation failed" or "pg_config executable not found"

**Cause**: PostgreSQL development libraries not installed.

**Solutions**:

**Windows**:
```bash
pip install psycopg2-binary
```

**Mac**:
```bash
brew install postgresql
pip install psycopg2-binary
```

**Linux**:
```bash
sudo apt-get install libpq-dev
pip install psycopg2
```

---

### Issue: "Address already in use" (Port 8000)

**Cause**: Another process is using port 8000.

**Solutions**:

**Windows**:
```powershell
# Find process using port 8000
netstat -ano | findstr :8000

# Kill the process (replace PID with actual process ID)
taskkill /PID <PID> /F
```

**Mac/Linux**:
```bash
# Find and kill process
lsof -ti:8000 | xargs kill -9
```

**Alternative**: Change port in `backend/app/config.py`:
```python
API_PORT: int = 8001  # Change to different port
```

---

### Issue: "Downloading sentence-transformers model is stuck/slow"

**Cause**: Large model download (~100MB) on slow connection.

**Solutions**:
- Be patient - this only happens once
- Model is cached after first download
- Try different internet connection
- Pre-download manually:

```python
# Run this once:
python
>>> from sentence_transformers import SentenceTransformer
>>> model = SentenceTransformer('all-MiniLM-L6-v2')
>>> exit()
```

---

### Issue: "File not found" when uploading resume

**Cause**: Uploads directory doesn't exist or wrong permissions.

**Solutions**:
```bash
# Create uploads directory
mkdir backend/uploads

# Windows: Set permissions
icacls backend\uploads /grant Users:F

# Mac/Linux: Set permissions
chmod 777 backend/uploads
```

---

### Issue: init_db.py fails with "no such table"

**Cause**: Tables not created before running init_db.py.

**Solution**:
```python
# Tables are created automatically by main.py
# Either:

# Option 1: Run main.py first (it creates tables)
python main.py
# Then Ctrl+C to stop
# Then run init_db.py

# Option 2: Force table creation
python
>>> from app.database import Base, engine
>>> Base.metadata.create_all(bind=engine)
>>> exit()
```

---

## 🎨 Frontend Issues

### Issue: "npm install fails" or "ERESOLVE unable to resolve dependency tree"

**Solutions**:

1. **Delete and retry**:
```bash
# Delete node_modules and package-lock.json
rm -rf node_modules package-lock.json  # Mac/Linux
rmdir /s /q node_modules & del package-lock.json  # Windows

# Reinstall
npm install
```

2. **Use legacy peer deps**:
```bash
npm install --legacy-peer-deps
```

3. **Clear npm cache**:
```bash
npm cache clean --force
npm install
```

---

### Issue: "Module not found: Can't resolve '@/lib/api'" or similar

**Cause**: TypeScript path aliases not configured.

**Solution**:
Verify `tsconfig.json` has:
```json
{
  "compilerOptions": {
    "paths": {
      "@/*": ["./*"]
    }
  }
}
```

Restart dev server:
```bash
npm run dev
```

---

### Issue: "Port 3000 already in use"

**Solutions**:

**Windows**:
```powershell
netstat -ano | findstr :3000
taskkill /PID <PID> /F
```

**Mac/Linux**:
```bash
lsof -ti:3000 | xargs kill -9
```

**Alternative**: Use different port:
```bash
PORT=3001 npm run dev
```

---

### Issue: "Failed to fetch" or "Network Error" when uploading resume

**Cause**: Frontend can't connect to backend.

**Solutions**:

1. **Verify backend is running**:
```bash
# Test in browser or curl
curl http://localhost:8000/health
```

2. **Check CORS settings** in `backend/main.py`:
```python
CORS_ORIGINS = ["http://localhost:3000"]
```

3. **Verify API URL** in `frontend/.env.local`:
```ini
NEXT_PUBLIC_API_URL=http://localhost:8000
```

4. **Restart both servers**.

---

### Issue: Styling not working / Tailwind not applied

**Solutions**:

1. **Verify Tailwind is installed**:
```bash
npm list tailwindcss
```

2. **Check tailwind.config.js content paths**:
```javascript
content: [
  './app/**/*.{js,ts,jsx,tsx,mdx}',
  './components/**/*.{js,ts,jsx,tsx,mdx}',
],
```

3. **Restart dev server**:
```bash
npm run dev
```

4. **Clear Next.js cache**:
```bash
rm -rf .next
npm run dev
```

---

## 🔄 Full System Issues

### Issue: "Everything is set up but matching doesn't work"

**Debugging Steps**:

1. **Check backend logs** for errors during matching
2. **Verify embeddings exist**:
```bash
# In PostgreSQL
psql -U postgres -d job_matcher
SELECT COUNT(*) FROM jobs WHERE embedding IS NOT NULL;
```

3. **Verify resume was parsed**:
```bash
# Check API
curl http://localhost:8000/resumes/1
# Should show skills, education, experience
```

4. **Test matching directly**:
```bash
curl http://localhost:8000/matches/1?top_n=5
```

---

### Issue: "Match scores are all very low or very high"

**Causes & Solutions**:

**All scores ~0-10%**:
- Resume parsing failed - no skills extracted
- Check: Are skills in the resume using common tech terms?
- Solution: Add more recognizable skills to resume

**All scores ~90-100%**:
- Embeddings might not be generated correctly
- Solution: Re-run `python init_db.py` to regenerate embeddings

**Reasonable but unexpected**:
- This is semantic matching - it's not keyword matching
- The model considers context, not just exact words
- This is expected behavior!

---

### Issue: "Uploaded resume shows 0 skills found"

**Causes**:
- PDF is image-based (scanned), not text
- Skills not in the predefined keyword list
- Unusual formatting in resume

**Solutions**:

1. **Verify PDF has text**:
```python
import pdfplumber
with pdfplumber.open('resume.pdf') as pdf:
    text = pdf.pages[0].extract_text()
    print(text)  # Should show actual text
```

2. **Add more skills** to `backend/app/services/resume_parser.py`:
```python
self.skill_keywords = {
    'python', 'java', 'javascript',
    # Add your skills here:
    'your_skill_1', 'your_skill_2',
}
```

3. **Use text-based PDF** (not scanned image).

---

## 🚀 Performance Issues

### Issue: "First resume upload is very slow (30+ seconds)"

**Cause**: First-time model download and initialization.

**This is normal!** 
- Sentence transformer downloads model (~100MB)
- Model initialization takes time
- Subsequent uploads will be much faster

---

### Issue: "Matching is slow for many jobs"

**Optimization options**:

1. **Reduce number of jobs in database**
2. **Add indexing**:
```python
# In backend/app/models/job.py
from sqlalchemy import Index

class Job(Base):
    # ... existing code ...
    
    __table_args__ = (
        Index('idx_job_type', 'job_type'),
    )
```

3. **Implement caching** (advanced):
```python
from functools import lru_cache

@lru_cache(maxsize=100)
def get_job_embeddings():
    # Cache embeddings in memory
    pass
```

---

## 🔐 Security Issues

### Issue: "CORS errors in browser console"

**Solution**:
Update `backend/app/config.py`:
```python
CORS_ORIGINS: List[str] = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    # Add your deployed frontend URL
]
```

---

### Issue: "SQL injection concerns"

**Good news**: You're protected!
- SQLAlchemy ORM handles SQL injection
- Pydantic validates input data
- No raw SQL queries in code

---

## 📝 Data Issues

### Issue: "Sample jobs not loading"

**Solution**:
```bash
cd backend

# Check if sample_jobs.json exists
ls data/sample_jobs.json  # Mac/Linux
dir data\sample_jobs.json  # Windows

# Verify JSON is valid
python -c "import json; print(json.load(open('data/sample_jobs.json')))"

# Re-run initialization
python init_db.py
```

---

### Issue: "Database tables not created"

**Solution**:
```python
# Force table creation
python
>>> from app.database import Base, engine
>>> Base.metadata.drop_all(bind=engine)  # Warning: Deletes all data!
>>> Base.metadata.create_all(bind=engine)
>>> exit()
```

---

## 🌐 Deployment Issues

### Issue: "Works locally but fails in production"

**Common causes**:

1. **Environment variables not set**
   - Check `.env` settings in production
   - Ensure `DATABASE_URL` is correct

2. **Database not accessible**
   - Verify database is publicly accessible
   - Check firewall rules

3. **CORS not configured for production domain**
   - Add production URL to `CORS_ORIGINS`

4. **File upload path issues**
   - Ensure writable directory for uploads
   - Consider using cloud storage (S3, etc.)

---

## 🆘 Still Stuck?

### Get Help:

1. **Check logs**:
```bash
# Backend logs
python main.py
# Look for error messages

# Frontend logs
npm run dev
# Check browser console (F12)
```

2. **Verify all prerequisites**:
```bash
python --version  # Should be 3.9+
node --version    # Should be 18+
psql --version    # Should be 14+
```

3. **Start fresh**:
```bash
# Backend
rm -rf venv
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate
pip install -r requirements.txt

# Frontend
rm -rf node_modules .next
npm install
```

4. **Check project structure**:
```bash
# Should see all these directories
ls -la
# backend/
# frontend/
# data/
# README.md
# etc.
```

---

## ✅ Prevention Tips

**Before you start**:
- ✅ Install all prerequisites first
- ✅ Create database before running init_db.py
- ✅ Configure .env files correctly
- ✅ Run backend before frontend
- ✅ Test each component separately

**During development**:
- ✅ Read error messages carefully
- ✅ Check terminal output
- ✅ Use browser dev tools (F12)
- ✅ Test API endpoints with curl/Postman
- ✅ Keep backend and frontend terminals separate

**Common mistakes to avoid**:
- ❌ Running commands from wrong directory
- ❌ Forgetting to activate virtual environment
- ❌ Not setting database password in .env
- ❌ Not creating database in PostgreSQL
- ❌ Starting frontend before backend

---

## 📞 Quick Reference

**Backend not starting?**
1. Check virtual environment activated
2. Verify .env has correct DATABASE_URL
3. Ensure PostgreSQL is running
4. Try different port if 8000 is busy

**Frontend not starting?**
1. Run `npm install` again
2. Delete .next folder
3. Check .env.local has API_URL
4. Try different port if 3000 is busy

**Matching not working?**
1. Verify backend is running
2. Check resume upload succeeded
3. Ensure jobs are in database
4. Look at API response in browser dev tools

**Still issues?**
- Read the error message slowly
- Google the specific error
- Check file paths are correct
- Restart everything

---

You've got this! 💪 Most issues are simple configuration problems that are easy to fix once identified.
