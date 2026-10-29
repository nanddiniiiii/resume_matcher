import { defineConfig } from '@playwright/test'
import path from 'node:path'
import os from 'node:os'

const backend = path.resolve('../backend')
const python = process.env.E2E_PYTHON || path.join(backend, 'venv', process.platform === 'win32' ? 'Scripts/python.exe' : 'bin/python')
const dbFile = path.join(os.tmpdir(), `matcher-browser-${process.pid}.db`).replace(/\\/g, '/')
export default defineConfig({
  testDir: './e2e',
  timeout: 180_000,
  workers: 1,
  use: {
    baseURL: 'http://localhost:3123',
    channel: process.env.E2E_BROWSER_CHANNEL || undefined,
    trace: 'retain-on-failure',
  },
  webServer: [
    {
      command: `"${python}" -m uvicorn main:app --host 127.0.0.1 --port 8123`,
      cwd: backend,
      url: 'http://localhost:8123/health',
      timeout: 60_000,
      env: {
        DATABASE_URL: `sqlite:///${dbFile}`,
        UPLOAD_DIR: path.join(os.tmpdir(), `matcher-browser-uploads-${process.pid}`),
        SECRET_KEY: 'browser-tests-only-secret-at-least-32-characters',
        ADMIN_EMAILS: '["browser-admin@example.com"]',
        CORS_ORIGINS: '["http://localhost:3123"]',
        DEBUG: 'false',
      },
    },
    {
      command: 'npm run dev -- --port 3123',
      url: 'http://localhost:3123',
      timeout: 120_000,
      env: { NEXT_PUBLIC_API_URL: 'http://localhost:8123' },
    },
  ],
})
