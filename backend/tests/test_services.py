import pytest
from app.services.resume_parser import ResumeParser
from app.services.job_matcher import JobMatcher
from app.services.resume_analyzer import ResumeAnalyzerService


def test_skill_boundaries():
    parser = ResumeParser()
    skills = parser.extract_skills("Django JavaScript C++ C# Python")
    assert {"django", "javascript", "c++", "c#", "python"} <= set(skills)
    assert "go" not in skills
    assert "java" not in skills
    assert skills == sorted(skills)


def test_scoring_counts_overlap_not_total_skills(monkeypatch):
    service = ResumeAnalyzerService()
    monkeypatch.setattr(JobMatcher, "generate_embedding", lambda self, text: [1.0, 0.0])
    result = service.analyze_resume_for_job("Python skills", "SQL Java", ["SQL", "Java"], ["Python", "CSS", "HTML", "Docker"])
    assert result["skill_match_rate"] == 0
    assert result["ats_score"] <= 60


def test_model_failure_does_not_fabricate_score(monkeypatch):
    def fail(self, text):
        raise RuntimeError("model unavailable")
    monkeypatch.setattr(JobMatcher, "generate_embedding", fail)
    with pytest.raises(RuntimeError, match="no score"):
        ResumeAnalyzerService()._calculate_ats_score("Python", "Python", ["Python"], ["Python"])


def test_cosine_and_ranking():
    matcher = JobMatcher()
    assert matcher.calculate_similarity([1, 0], [0, 1]) == 0
    jobs = [{"id": 1, "title": "Unrelated", "embedding": [0, 1], "required_skills": []}, {"id": 2, "title": "Relevant", "embedding": [1, 0], "required_skills": ["Python"]}]
    result = matcher.rank_jobs([1, 0], ["Python"], jobs)
    assert [match["job"]["id"] for match in result] == [2]


def test_production_rejects_placeholder_secret():
    from app.config import Settings
    with pytest.raises(ValueError, match="SECRET_KEY"):
        Settings(APP_ENV="production", SECRET_KEY="replace-with-a-random-secret-at-least-32-characters")


def test_skill_overlap_is_bounded_and_deduplicated():
    matching, missing, rate = JobMatcher().analyze_skill_match([" python ", "Python", "CSS"], ["Python", "python", "SQL"])
    assert len(matching) == 1
    assert missing == ["SQL"]
    assert rate == 0.5
