# Quick Start Script for Windows
# Run this after installing Python, Node.js, and PostgreSQL

Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "   AI Job Matcher - Quick Setup Script" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host ""

# Check prerequisites
Write-Host "Checking prerequisites..." -ForegroundColor Yellow

# Check Python
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Python not found. Please install Python 3.9+" -ForegroundColor Red
    exit 1
}

# Check Node.js
try {
    $nodeVersion = node --version 2>&1
    Write-Host "✓ Node.js found: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Node.js not found. Please install Node.js 18+" -ForegroundColor Red
    exit 1
}

# Check PostgreSQL
try {
    $pgVersion = psql --version 2>&1
    Write-Host "✓ PostgreSQL found: $pgVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ PostgreSQL not found. Please install PostgreSQL 14+" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "   Backend Setup" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host ""

# Backend setup
Set-Location backend

Write-Host "Creating Python virtual environment..." -ForegroundColor Yellow
python -m venv venv

Write-Host "Activating virtual environment..." -ForegroundColor Yellow
.\venv\Scripts\Activate.ps1

Write-Host "Installing Python dependencies..." -ForegroundColor Yellow
Write-Host "(This may take 5-10 minutes)" -ForegroundColor Gray
pip install -r requirements.txt

Write-Host "Downloading spaCy language model..." -ForegroundColor Yellow
python -m spacy download en_core_web_sm

Write-Host ""
Write-Host "✓ Backend dependencies installed!" -ForegroundColor Green
Write-Host ""

# Check if .env exists
if (-Not (Test-Path .env)) {
    Write-Host "Creating .env file..." -ForegroundColor Yellow
    Copy-Item .env.example .env
    Write-Host "⚠ IMPORTANT: Edit backend\.env and set your PostgreSQL password!" -ForegroundColor Yellow
    Write-Host "   DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/job_matcher" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "   Frontend Setup" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host ""

# Frontend setup
Set-Location ..\frontend

Write-Host "Installing Node.js dependencies..." -ForegroundColor Yellow
Write-Host "(This may take 3-5 minutes)" -ForegroundColor Gray
npm install

# Check if .env.local exists
if (-Not (Test-Path .env.local)) {
    Write-Host "Creating .env.local file..." -ForegroundColor Yellow
    Copy-Item .env.local.example .env.local
}

Write-Host ""
Write-Host "✓ Frontend dependencies installed!" -ForegroundColor Green
Write-Host ""

# Return to root
Set-Location ..

Write-Host ""
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "   Setup Complete!" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Create PostgreSQL database:" -ForegroundColor White
Write-Host "   psql -U postgres -c 'CREATE DATABASE job_matcher;'" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Edit backend\.env with your database password" -ForegroundColor White
Write-Host ""
Write-Host "3. Initialize database:" -ForegroundColor White
Write-Host "   cd backend" -ForegroundColor Gray
Write-Host "   .\venv\Scripts\Activate.ps1" -ForegroundColor Gray
Write-Host "   python init_db.py" -ForegroundColor Gray
Write-Host ""
Write-Host "4. Start backend (Terminal 1):" -ForegroundColor White
Write-Host "   cd backend" -ForegroundColor Gray
Write-Host "   .\venv\Scripts\Activate.ps1" -ForegroundColor Gray
Write-Host "   python main.py" -ForegroundColor Gray
Write-Host ""
Write-Host "5. Start frontend (Terminal 2):" -ForegroundColor White
Write-Host "   cd frontend" -ForegroundColor Gray
Write-Host "   npm run dev" -ForegroundColor Gray
Write-Host ""
Write-Host "6. Open browser: http://localhost:3000" -ForegroundColor White
Write-Host ""
Write-Host "For detailed instructions, see SETUP_GUIDE.md" -ForegroundColor Cyan
Write-Host ""
