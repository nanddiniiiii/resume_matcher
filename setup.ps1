$ErrorActionPreference = 'Stop'
$projectRoot = $PSScriptRoot
function Run-Checked {
    param([scriptblock]$Command)
    & $Command
    if ($LASTEXITCODE -ne 0) { throw "Command failed with exit code $LASTEXITCODE" }
}
foreach ($command in @('python', 'node', 'npm')) {
    if (-not (Get-Command $command -ErrorAction SilentlyContinue)) { throw "$command is required. See README.md." }
}
Push-Location $projectRoot
try {
    Run-Checked { python -m venv backend/venv }
    Run-Checked { & "$projectRoot/backend/venv/Scripts/python.exe" -m pip install -r backend/requirements.txt }
    if (-not (Test-Path -LiteralPath backend/.env)) { Copy-Item -LiteralPath backend/.env.example -Destination backend/.env }
    Push-Location frontend
    try {
        Run-Checked { npm ci }
        if (-not (Test-Path -LiteralPath .env.local)) { Copy-Item -LiteralPath .env.local.example -Destination .env.local }
    } finally { Pop-Location }
    Write-Host 'Dependencies installed. Configure backend/.env, initialize the database, then follow README.md to start both services.'
} finally { Pop-Location }
