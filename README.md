# Resume Matcher

A resume-based job discovery app built with FastAPI, PostgreSQL and Next.js. Upload a PDF, compare it with job descriptions, review skill overlap, and keep track of saved jobs and applications.

I built this project to connect document parsing, sentence embeddings and a usable job-search workflow. It uses a pretrained model; it does not train a hiring model or predict whether someone will be hired.

## How matching works

1. `pdfplumber` extracts selectable text from the uploaded PDF.
2. The parser identifies skills and basic education/experience entries using keyword and pattern matching.
3. `sentence-transformers/all-MiniLM-L6-v2` encodes the prepared resume text into a 384-dimensional vector. Job descriptions are encoded with the same model.
4. Cosine similarity ranks active jobs. Results below `SIMILARITY_THRESHOLD` are excluded.
5. Skill overlap and missing skills provide additional context for each result. They explain explicit keyword overlap, rather than the internal decisions of the Transformer.

Ranking currently uses semantic similarity alone. The separate resume relevance score combines skill overlap (40 points), keyword coverage (30), and semantic similarity (30). It is heuristic feedback, not a measured employer ATS score or a hiring probability. Model failures return an error instead of a substitute score.

Long inputs are subject to the model's token limit. The resume representation emphasizes extracted skills, education, experience and an initial text excerpt. This can miss information later in a document; improving document coverage and evaluating ranking quality are the next priorities.

## Features

- Authenticated PDF upload, resume history and deletion. Each user can access only their own resumes and matches.
- Ranked job matches with skill overlap, gaps, source links and resume-specific analysis.
- Text, skill, location and job-type filters.
- Saved jobs, application statuses and account activity.
- RemoteOK ingestion with HTML cleanup, source IDs, refreshed embeddings and expiration handling.
- Administrator controls for job writes, ingestion and expiration management.
- Responsive interface with a persistent light/dark preference.

RemoteOK is the only implemented external source. Adzuna is listed as unimplemented. The jobs in `data/sample_jobs.json` and `backend/add_more_jobs.py` are demonstration records, not live vacancies. Imported listings are assigned a local 30-day expiration window; that is not a source-confirmed closing date.

## Run locally

Use Python 3.11–3.13, Node.js 20.9 or later, and PostgreSQL. Development was checked on Windows with Python 3.13, Node.js 24 and PostgreSQL 18.

### Backend

Create a PostgreSQL database named `job_matcher`, then run from the repository root:

```powershell
python -m venv backend/venv
backend/venv/Scripts/python -m pip install -r backend/requirements.txt
Copy-Item backend/.env.example backend/.env
```

Edit `backend/.env` with your database URL and a random secret:

```text
DATABASE_URL=postgresql://username:password@localhost:5432/job_matcher
SECRET_KEY=<generate a random value of at least 32 characters>
CORS_ORIGINS=["http://localhost:3000"]
ADMIN_EMAILS=["your-account@example.com"]
```

Generate the secret with `python -c "import secrets; print(secrets.token_urlsafe(48))"`. Register the same email through the app to use administrator controls. Administrator status comes from server configuration, never from registration input.

```powershell
cd backend
venv/Scripts/python check_model.py
venv/Scripts/python init_db.py
venv/Scripts/python main.py
```

`check_model.py` downloads and loads the configured model. Initial download requires internet access; subsequent runs use the Hugging Face cache. `init_db.py` creates tables and loads sample jobs with real embeddings. Repeating it skips existing title/company pairs. No spaCy model is needed.

The API runs at `http://localhost:8000`, documentation at `/docs`, and database readiness at `/health`. The app also creates missing tables at startup, but does not alter existing table schemas.

For a lightweight local demo, `DATABASE_URL=sqlite:///./job_matcher.db` is supported. PostgreSQL is the main deployment target. On macOS/Linux, use `backend/venv/bin/python` instead of the Windows interpreter path.

### Frontend

In another terminal:

```powershell
cd frontend
Copy-Item .env.local.example .env.local
npm ci
npm run dev
```

Open `http://localhost:3000`, register an account and upload a PDF with selectable text. Scanned PDFs need OCR before upload. The default upload limit is 5 MiB.

All frontend requests use `NEXT_PUBLIC_API_URL`, defaulting to `http://localhost:8000`. Set it before building if the API is hosted elsewhere. It is a public browser setting, so it must not contain credentials.

### Existing databases

Back up an existing database before running migrations. The legacy scripts are PostgreSQL-specific and must be run from `backend/`:

```powershell
venv/Scripts/python migrate_auth.py
venv/Scripts/python migrate_database_improvements.py
venv/Scripts/python migrate_scraping_fields.py
```

Legacy accounts without password hashes are disabled rather than assigned a shared password. A trusted administrator must arrange account recovery. Versioned schema migrations and a password-reset workflow remain future work.

## Checks

```powershell
backend/venv/Scripts/python -m pip install -r backend/requirements-dev.txt
backend/venv/Scripts/python -m pytest backend/tests -q
backend/venv/Scripts/python -m ruff check backend/app backend/main.py --select F
cd frontend
npm run lint
npm run typecheck
npm run build
npm audit
```

The default backend tests use a temporary SQLite database and controlled embeddings to check API behavior without downloading a model. Set `TEST_DATABASE_URL` to an empty disposable PostgreSQL database to check that database path. Tests create and drop application tables, so never point them at a database containing useful data. Set `RUN_MODEL_TESTS=1` to exercise route workflows with actual Transformer embeddings. Some service unit tests still use controlled vectors to test specific calculations and failures.

The browser workflow uses a temporary SQLite database and actual model inference. Install a Playwright browser with `npx playwright install chromium` from `frontend/`, then run `npm run test:e2e`. On Windows with Microsoft Edge installed, set `$env:E2E_BROWSER_CHANNEL='msedge'` instead. The test starts its own backend on port 8123 and frontend on port 3123. Set `E2E_PYTHON` if your backend interpreter is outside `backend/venv`. Warm the model cache first with `check_model.py`; `HF_HUB_OFFLINE=1` can then be used to test without model-hub requests.

GitHub Actions runs backend regression checks against PostgreSQL and frontend lint, type checking and a production build. See [the audit](docs/AUDIT.md) for findings, locally executed checks and remaining work.

## Configuration and operating limits

- `APP_ENV=production` rejects missing, short or placeholder secrets. Keep a stable secret in all server processes; the temporary development fallback invalidates sessions on restart.
- `ADMIN_EMAILS` and `CORS_ORIGINS` use JSON arrays in `.env`.
- Job mutations and scraper controls require an administrator account. Reading job listings is public.
- Scraping runs as an in-process background task with its own database session. `/api/scraper/status` reports the current run and last result. The run lock is per process, so use one API worker for scraping or add an external queue before scaling it.
- Embeddings are stored as JSON and ranked in application memory. This is suitable for a small catalog; use a vector index and batching for a large one.
- Changing the embedding model requires regenerating both job and resume embeddings.
- Browser authentication uses a JavaScript-readable bearer-token cookie. A server-managed HttpOnly session, rate limiting, password recovery and deployment-specific request limits should be added before a public launch.

## Repository

```text
backend/app/api/       HTTP routes and validation
backend/app/services/ PDF parsing, matching, analysis and ingestion
backend/app/models/   SQLAlchemy models
backend/tests/        API and service regressions
frontend/app/         Next.js pages
frontend/components/  Upload, matching and analysis UI
frontend/contexts/    Authentication and theme state
frontend/lib/         API configuration, client and types
data/                 Demonstration job records
docs/AUDIT.md         Review findings and follow-up work
```

The older feature and UI documents at the repository root are historical notes. This README describes the current setup and supported behavior.
