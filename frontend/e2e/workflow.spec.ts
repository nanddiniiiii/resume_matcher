import { test, expect } from '@playwright/test'

function resumePdf(): Buffer {
  const text = 'BT /F1 12 Tf 50 750 Td (Python SQL FastAPI developer experience education skills projects) Tj ET'
  const objects = ['<< /Type /Catalog /Pages 2 0 R >>', '<< /Type /Pages /Kids [3 0 R] /Count 1 >>', '<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>', '<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>', `<< /Length ${text.length} >>\nstream\n${text}\nendstream`]
  let pdf = '%PDF-1.4\n'
  const offsets = [0]
  objects.forEach((object, i) => { offsets.push(Buffer.byteLength(pdf)); pdf += `${i + 1} 0 obj\n${object}\nendobj\n` })
  const xref = Buffer.byteLength(pdf)
  pdf += 'xref\n0 6\n0000000000 65535 f \n'
  offsets.slice(1).forEach(offset => { pdf += `${String(offset).padStart(10, '0')} 00000 n \n` })
  pdf += `trailer << /Size 6 /Root 1 0 R >>\nstartxref\n${xref}\n%%EOF`
  return Buffer.from(pdf)
}

test('register, upload, analyze, save, track and restore session', async ({ page, request }) => {
  const errors: string[] = []
  page.on('pageerror', error => errors.push(error.message))
  const api = 'http://localhost:8123'
  const admin = { email: 'browser-admin@example.com', password: 'browser-test-password', name: 'Browser Admin' }
  expect((await request.post(`${api}/api/auth/register`, { data: admin })).ok()).toBeTruthy()
  const login = await request.post(`${api}/api/auth/login/json`, { data: admin })
  const { access_token } = await login.json()
  const seeded = await request.post(`${api}/api/jobs/`, {
    headers: { Authorization: `Bearer ${access_token}` },
    timeout: 120_000,
    data: { title: 'Python Backend Engineer', company: 'Browser Test Example', description: 'Develop Python FastAPI REST APIs with PostgreSQL SQL and Docker.', required_skills: ['Python', 'SQL', 'FastAPI'], location: 'Remote', job_type: 'full-time' },
  })
  expect(seeded.ok()).toBeTruthy()
  await page.goto('/register')
  await page.getByLabel('Full Name').fill('Browser Candidate')
  await page.getByLabel('Email address').fill('browser-candidate@example.com')
  await page.getByLabel('Password', { exact: true }).fill('browser-candidate-password')
  await page.getByRole('button', { name: 'Create account', exact: true }).click()
  await expect(page.getByText('Upload Your Resume', { exact: true })).toBeVisible({ timeout: 30_000 })
  await page.locator('input[type=file]').setInputFiles({ name: 'resume.pdf', mimeType: 'application/pdf', buffer: resumePdf() })
  await page.getByRole('button', { name: 'Analyze Resume & Find Matches' }).click()
  await expect(page.getByRole('heading', { name: 'Your Top Job Matches' })).toBeVisible({ timeout: 60_000 })
  await expect(page.getByText('Python Backend Engineer', { exact: true })).toBeVisible()
  await page.getByRole('button', { name: /Full Analysis/ }).click()
  await expect(page.getByRole('heading', { name: 'Resume relevance score' })).toBeVisible()
  await expect(page.getByText('Heuristic feedback, not a hiring probability or an employer ATS result.')).toBeVisible()
  await page.getByRole('button', { name: 'Close', exact: true }).click()
  await page.getByRole('button', { name: /Save Job/ }).click()
  await page.getByRole('link', { name: 'Saved Jobs', exact: true }).click()
  await expect(page.getByText('Python Backend Engineer', { exact: true })).toBeVisible()
  await page.getByRole('link', { name: 'Upload Resume', exact: true }).click()
  const newUpload = page.getByRole('button', { name: 'Upload New Resume', exact: true })
  if (await newUpload.isVisible()) await newUpload.click()
  await page.locator('input[type=file]').setInputFiles({ name: 'resume.pdf', mimeType: 'application/pdf', buffer: resumePdf() })
  await page.getByRole('button', { name: 'Analyze Resume & Find Matches' }).click()
  await expect(page.getByRole('heading', { name: 'Your Top Job Matches' })).toBeVisible({ timeout: 60_000 })
  await page.getByRole('button', { name: /Track Application/ }).click()
  await expect(page).toHaveURL(/applications/)
  await expect(page.getByText('Python Backend Engineer', { exact: true })).toBeVisible()
  await page.reload()
  await expect(page.getByText('Python Backend Engineer', { exact: true })).toBeVisible()
  await page.getByTitle('Switch to dark mode').click()
  await expect(page.locator('html')).toHaveClass(/dark/)
  await page.reload()
  await expect(page.locator('html')).toHaveClass(/dark/)
  expect(errors).toEqual([])
})
