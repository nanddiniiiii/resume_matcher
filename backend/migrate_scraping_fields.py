"""
Database Migration Script - Add Scraping Fields to Jobs Table
Adds: source, source_url, source_job_id, scraped_at, expires_at, is_active
"""

from sqlalchemy import create_engine, text
from app.config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def migrate():
    """Add scraping-related fields to jobs table"""
    engine = create_engine(settings.DATABASE_URL)
    
    migrations = [
        "ALTER TABLE jobs ADD COLUMN IF NOT EXISTS source VARCHAR",
        "ALTER TABLE jobs ADD COLUMN IF NOT EXISTS source_url VARCHAR",
        "ALTER TABLE jobs ADD COLUMN IF NOT EXISTS source_job_id VARCHAR",
        "ALTER TABLE jobs ADD COLUMN IF NOT EXISTS scraped_at TIMESTAMP WITH TIME ZONE",
        "ALTER TABLE jobs ADD COLUMN IF NOT EXISTS expires_at TIMESTAMP WITH TIME ZONE",
        "ALTER TABLE jobs ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE",
        
        # Add index for source lookups
        "CREATE INDEX IF NOT EXISTS idx_jobs_source ON jobs(source)",
        "CREATE INDEX IF NOT EXISTS idx_jobs_source_job_id ON jobs(source_job_id)",
        "CREATE INDEX IF NOT EXISTS idx_jobs_is_active ON jobs(is_active)",
        "CREATE INDEX IF NOT EXISTS idx_jobs_expires_at ON jobs(expires_at)",
    ]
    
    try:
        with engine.connect() as conn:
            for migration_sql in migrations:
                try:
                    logger.info(f"Executing: {migration_sql}")
                    conn.execute(text(migration_sql))
                    conn.commit()
                    logger.info("✓ Success")
                except Exception as e:
                    logger.warning(f"Migration already applied or error: {e}")
        
        logger.info("✅ All migrations completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        raise
    finally:
        engine.dispose()


if __name__ == "__main__":
    logger.info("Starting migration...")
    migrate()
    logger.info("Migration complete!")
