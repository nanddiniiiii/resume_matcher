"""
Script to initialize the database with sample job data.
Run this after setting up the database.
"""
import sys
import os
import json

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal, engine, Base
from app.models import Job
from app.services.job_matcher import JobMatcher

def init_db():
    """Create all database tables."""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✓ Database tables created")

def load_sample_jobs():
    """Load sample jobs from JSON file into database."""
    db = SessionLocal()
    job_matcher = JobMatcher()
    
    try:
        # Check if jobs already exist
        existing_count = db.query(Job).count()
        if existing_count > 0:
            print(f"Database already contains {existing_count} jobs")
            response = input("Do you want to add more jobs anyway? (y/n): ")
            if response.lower() != 'y':
                print("Skipping job loading")
                return
        
        # Load jobs from JSON
        json_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'data',
            'sample_jobs.json'
        )
        
        with open(json_path, 'r') as f:
            jobs_data = json.load(f)
        
        print(f"Loading {len(jobs_data)} sample jobs...")
        
        # Create jobs with embeddings
        for job_data in jobs_data:
            # Generate embedding
            job_text = job_matcher.prepare_job_text(job_data)
            job_embedding = job_matcher.generate_embedding(job_text)
            
            # Create job
            job = Job(
                title=job_data['title'],
                company=job_data['company'],
                description=job_data['description'],
                required_skills=job_data['required_skills'],
                location=job_data.get('location'),
                job_type=job_data.get('job_type'),
                embedding=job_embedding
            )
            
            db.add(job)
            print(f"  ✓ Added: {job_data['title']} at {job_data['company']}")
        
        db.commit()
        print(f"\n✓ Successfully loaded {len(jobs_data)} jobs into database")
        
    except FileNotFoundError:
        print(f"Error: Could not find sample_jobs.json at {json_path}")
    except Exception as e:
        print(f"Error loading jobs: {str(e)}")
        db.rollback()
    finally:
        db.close()

def main():
    """Main initialization function."""
    print("=" * 50)
    print("AI Job Matcher - Database Initialization")
    print("=" * 50)
    
    # Initialize database
    init_db()
    
    # Load sample jobs
    load_sample_jobs()
    
    print("\n" + "=" * 50)
    print("Initialization complete!")
    print("=" * 50)
    print("\nYou can now:")
    print("1. Start the backend server: python main.py")
    print("2. Upload resumes via the API")
    print("3. Get job recommendations")

if __name__ == "__main__":
    main()
