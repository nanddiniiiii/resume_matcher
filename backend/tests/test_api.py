from pathlib import Path

import pytest

from conftest import account

from app.database import SessionLocal

from app.models import Job

from app.config import settings



def test_health(client):

    assert client.get("/health").json()["database"] == "connected"



def test_auth_and_profile(client, user):

    assert client.get("/api/auth/me", headers=user).status_code == 200

    result = client.put("/api/auth/me", headers=user, json={"name": "Updated"})

    assert result.json()["name"] == "Updated"

    assert client.post("/api/auth/login/json", json={"email": "candidate@example.com", "password": "wrong"}).status_code == 401



@pytest.mark.parametrize("password", ["short", "a" * 73, "\u00e9" * 40])

def test_invalid_password(client, password):

    assert client.post("/api/auth/register", json={"email": "bad@example.com", "password": password}).status_code == 422



def test_resume_requires_login(client):

    assert client.post("/api/resumes/upload", files={"file": ("x.pdf", b"%PDF-invalid")}).status_code == 401

    assert client.get("/api/resumes/").status_code == 401



def test_resume_upload_and_ownership(client, user, resume):

    rid = resume["id"]

    assert "python" in resume["skills_found"]

    assert len(client.get("/api/resumes/", headers=user).json()) == 1

    stranger = account(client, "stranger@example.com")

    for method, path in [("get", f"/api/resumes/{rid}"), ("delete", f"/api/resumes/{rid}"), ("get", f"/api/matches/{rid}"), ("get", f"/api/matches/history/{rid}")]:

        assert getattr(client, method)(path, headers=stranger).status_code == 404

    assert client.get("/api/resumes/", headers=stranger).json() == []



@pytest.mark.parametrize("name,body,code", [("x.txt", b"abc", 400), ("x.pdf", b"not PDF", 400), ("x.pdf", b"%PDF-broken", 400)])

def test_invalid_upload_cleans_file(client, user, name, body, code):

    before = set(Path(settings.UPLOAD_DIR).glob("*"))

    assert client.post("/api/resumes/upload", headers=user, files={"file": (name, body)}).status_code == code

    assert set(Path(settings.UPLOAD_DIR).glob("*")) == before



def test_upload_limit(client, user, monkeypatch):

    monkeypatch.setattr(settings, "MAX_UPLOAD_SIZE", 8)

    assert client.post("/api/resumes/upload", headers=user, files={"file": ("x.pdf", b"%PDF-123456789")}).status_code == 413



def test_job_search_and_admin(client, user, job):

    assert client.get("/api/jobs/search", params={"skills": "Python"}).json()["total"] == 1

    assert client.get("/api/jobs/saved", headers=user).status_code == 200

    assert client.delete(f"/api/jobs/{job['id']}", headers=user).status_code == 403

    assert client.post("/api/scraper/run", headers=user).status_code == 403

    assert client.get("/api/jobs/", params={"limit": 0}).status_code == 422



def test_saved_jobs_and_applications(client, user, job, resume):

    jid, rid = job["id"], resume["id"]

    assert client.post(f"/api/jobs/{jid}/save", headers=user).status_code == 200

    saved = client.get("/api/jobs/saved", headers=user).json()

    assert saved["saved_jobs"][0]["job"]["skills_required"] == ["Python", "SQL"]

    app = client.post("/api/applications/", headers=user, json={"job_id": jid, "resume_id": rid}).json()

    aid = app["application_id"]

    assert client.put(f"/api/applications/{aid}", headers=user, json={"status": "interviewing"}).status_code == 200

    assert client.get("/api/users/stats", headers=user).json()["total_applications"] == 1

    assert client.delete(f"/api/resumes/{rid}", headers=user).status_code == 200

    assert client.get("/api/applications/", headers=user).json()["total"] == 1



def test_matching_and_analysis(client, user, job, resume):

    rid = resume["id"]

    result = client.get(f"/api/matches/{rid}", headers=user)

    assert result.status_code == 200, result.text

    assert result.json()["total_matches"] == 1

    assert client.get(f"/api/users/matches/{rid}", headers=user).json()["total"] == 1

    analysis = client.post("/api/resume-analyzer/analyze", headers=user, json={"resume_id": rid, "job_id": job["id"]})

    assert analysis.status_code == 200, analysis.text

    assert analysis.json()["skill_match_rate"] == 100

    assert client.get(f"/api/resume-analyzer/quick-tips/{job['id']}", headers=user).status_code == 200

    assert client.get(f"/api/matches/{rid}?top_n=-1", headers=user).status_code == 422

    with SessionLocal() as db:

        db.query(Job).filter(Job.id == job["id"]).update({"is_active": False})

        db.commit()

    assert client.get(f"/api/matches/{rid}", headers=user).json()["total_matches"] == 0



def test_admin_delete_related_records(client, user, admin, job, resume):

    client.post(f"/api/jobs/{job['id']}/save", headers=user)

    client.post("/api/applications/", headers=user, json={"job_id": job["id"]})

    assert client.delete(f"/api/jobs/{job['id']}", headers=admin).status_code == 200

    assert client.get("/api/jobs/saved", headers=user).json()["total"] == 0



@pytest.mark.parametrize("path", ["/api/jobs/saved", "/api/applications/", "/api/users/resumes"])

def test_pagination_validation(client, user, path):

    assert client.get(path, headers=user, params={"limit": 0}).status_code == 422



def test_inactive_user_is_rejected(client, user):
    from app.models import User
    with SessionLocal() as db:
        db.query(User).filter(User.email == "candidate@example.com").update({"is_active": False})
        db.commit()
    assert client.get("/api/auth/me", headers=user).status_code == 401


def test_scraper_status_and_background_session(client, admin, monkeypatch):
    from app.services.job_scraper import job_scraper_service
    from app.api import scraper
    monkeypatch.setattr(job_scraper_service, "scrape_all_sources", lambda db, limit_per_source: {"total_added": 0, "errors": []})
    assert client.post("/api/scraper/run", headers=admin).status_code == 200
    result = client.get("/api/scraper/status", headers=admin).json()
    assert result["sources_available"] == ["remoteok"]
    assert result["run"]["running"] is False
    assert result["run"]["last_result"]["total_added"] == 0
    assert client.post("/api/scraper/run?limit_per_source=-1", headers=admin).status_code == 422
    scraper._run_lock.acquire()
    try:
        assert client.post("/api/scraper/run", headers=admin).status_code == 409
    finally:
        scraper._run_lock.release()


def test_scraped_update_refreshes_embedding_and_expiry(client, monkeypatch):
    from datetime import datetime, timedelta, timezone
    from app.services.job_scraper import job_scraper_service
    now = datetime.now(timezone.utc)
    item = {"title": "Python", "company": "Example", "description": "Python developer", "required_skills": ["Python"], "location": "Remote", "job_type": "remote", "source": "remoteok", "source_url": "https://example.com/job", "source_job_id": "test-1", "scraped_at": now, "expires_at": now + timedelta(days=30), "is_active": True}
    with SessionLocal() as db:
        assert job_scraper_service.save_jobs_to_db([item], db)["added"] == 1
        item["description"] = "Updated Python job"
        item["expires_at"] = now + timedelta(days=60)
        assert job_scraper_service.save_jobs_to_db([item], db)["updated"] == 1
        job = db.query(Job).one()
        assert job.description == "Updated Python job"
        assert job.embedding
        job.expires_at = now - timedelta(days=1)
        db.commit()
        assert job_scraper_service.mark_expired_jobs(db) == 1
        db.refresh(job)
        assert job.is_active is False
