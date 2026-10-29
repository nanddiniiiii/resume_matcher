import os
import sys
import tempfile
from pathlib import Path

TEST_DIR = tempfile.TemporaryDirectory(prefix="resume-matcher-tests-")
os.environ["DATABASE_URL"] = os.environ.get("TEST_DATABASE_URL", "sqlite:///" + str(Path(TEST_DIR.name) / "test.db"))
os.environ["UPLOAD_DIR"] = str(Path(TEST_DIR.name) / "uploads")
os.environ["ADMIN_EMAILS"] = '["admin@example.com"]'
os.environ["SECRET_KEY"] = "regression-tests-only-secret-key-32-characters"
os.environ["DEBUG"] = "false"
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest
from fastapi.testclient import TestClient
from app.database import Base, engine
from app.services.job_matcher import JobMatcher
from main import app

@pytest.fixture
def client(monkeypatch):
    # Route tests isolate HTTP/database behavior from model downloads.
    # Real model inference is checked separately, not claimed by these tests.
    if os.environ.get("RUN_MODEL_TESTS") != "1":
        monkeypatch.setattr(JobMatcher, "generate_embedding", lambda self, text: [1.0, 0.0, 0.0])
    Base.metadata.drop_all(engine)
    with TestClient(app) as client:
        yield client


def account(client, email="candidate@example.com"):
    payload = {"email": email, "password": "correct-horse-123", "name": "Candidate"}
    assert client.post("/api/auth/register", json=payload).status_code == 201
    response = client.post("/api/auth/login/json", json=payload)
    assert response.status_code == 200, response.text
    return {"Authorization": "Bearer " + response.json()["access_token"]}

@pytest.fixture
def user(client):
    return account(client)

@pytest.fixture
def admin(client):
    return account(client, "admin@example.com")

@pytest.fixture
def job(client, admin):
    payload = {"title": "Python Developer", "company": "Example", "description": "Python SQL backend development", "required_skills": ["Python", "SQL"], "location": "Remote", "job_type": "full-time"}
    response = client.post("/api/jobs/", headers=admin, json=payload)
    assert response.status_code == 200, response.text
    return response.json()

@pytest.fixture
def resume(client, user):
    # Minimal valid PDF with actual selectable text; parsed by pdfplumber.
    content = b"BT /F1 12 Tf 50 750 Td (Python SQL developer experience education skills projects) Tj ET"
    objects = [b"<< /Type /Catalog /Pages 2 0 R >>", b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>", b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>", b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>", b"<< /Length " + str(len(content)).encode() + b" >>\nstream\n" + content + b"\nendstream"]
    pdf = b"%PDF-1.4\n"
    offsets = [0]
    for i, obj in enumerate(objects, 1):
        offsets.append(len(pdf))
        pdf += str(i).encode() + b" 0 obj\n" + obj + b"\nendobj\n"
    xref = len(pdf)
    pdf += b"xref\n0 6\n0000000000 65535 f \n" + b"".join(f"{offset:010d} 00000 n \n".encode() for offset in offsets[1:])
    pdf += b"trailer << /Size 6 /Root 1 0 R >>\nstartxref\n" + str(xref).encode() + b"\n%%EOF"
    response = client.post("/api/resumes/upload", headers=user, files={"file": ("resume.PDF", pdf, "application/pdf")})
    assert response.status_code == 200, response.text
    return response.json()
