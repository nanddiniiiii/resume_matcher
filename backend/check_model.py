"""Download/load the configured model and check a real embedding."""
from app.services.job_matcher import JobMatcher

if __name__ == "__main__":
    matcher = JobMatcher()
    vector = matcher.generate_embedding("Python backend development with SQL")
    print(f"Model ready: {len(vector)} dimensions")
