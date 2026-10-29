"""
Database schema improvements and new tables.
Run this migration to add indexes, saved jobs, and application tracking.
"""
from sqlalchemy import text
from app.database import Base, engine
from app.models import User, Resume, Job, JobMatch, SavedJob, JobApplication


def add_indexes():
    """Add performance indexes to existing tables."""
    from sqlalchemy import text
    
    with engine.begin() as conn:
        # Add indexes for better query performance
        try:
            # User indexes
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)"))
            
            # Resume indexes
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_resumes_user_id ON resumes(user_id)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_resumes_created_at ON resumes(created_at DESC)"))
            
            # Job indexes
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_jobs_title ON jobs(title)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_jobs_location ON jobs(location)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_jobs_created_at ON jobs(created_at DESC)"))
            
            # JobMatch indexes
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_matches_resume_id ON job_matches(resume_id)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_matches_job_id ON job_matches(job_id)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_matches_score ON job_matches(similarity_score DESC)"))
            
            conn.commit()
            print("✅ Indexes created successfully")
        except Exception as e:
            print(f"Index migration failed: {e}")
            raise


def run_migration():
    """Run all database migrations."""
    print("🚀 Starting database migration...")
    
    # Create new tables
    print("📊 Creating new tables (saved_jobs, job_applications)...")
    Base.metadata.create_all(bind=engine)
    
    # Add indexes
    print("⚡ Adding performance indexes...")
    add_indexes()
    
    print("✅ Migration completed successfully!")
    print("\nNew features available:")
    print("  - Saved Jobs: Users can bookmark jobs")
    print("  - Application Tracking: Track job application status")
    print("  - Performance Indexes: Faster queries")


if __name__ == "__main__":
    run_migration()
