"""
Job Scraper Service
Fetches real-time jobs from multiple sources (APIs and web scraping)
"""

import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import logging
import asyncio
import aiohttp
from sqlalchemy.orm import Session
from app.models import Job
from app.services.job_matcher import JobMatcher

logger = logging.getLogger(__name__)


class JobScraperService:
    """Service for scraping jobs from multiple sources"""
    
    def __init__(self):
        self.ml_service = JobMatcher()
        self.sources = {
            'remoteok': self.scrape_remoteok,
            'adzuna': self.scrape_adzuna,
        }
    
    def scrape_remoteok(self, limit: int = 50) -> List[Dict]:
        """
        Scrape jobs from RemoteOK (legal, public API-like endpoint)
        Returns remote tech jobs
        """
        jobs = []
        try:
            url = "https://remoteok.com/api"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # First item is metadata, skip it
            for job_data in data[1:limit+1]:
                try:
                    # Extract skills from tags
                    skills = []
                    if 'tags' in job_data and job_data['tags']:
                        skills = [tag for tag in job_data['tags'] if tag][:10]
                    
                    # Build description
                    description = job_data.get('description', '')
                    if not description and 'position' in job_data:
                        description = f"{job_data['position']} at {job_data.get('company', 'Company')}"
                    
                    if not description:
                        continue
                    
                    job = {
                        'title': job_data.get('position', 'Remote Position'),
                        'company': job_data.get('company', 'Company'),
                        'description': description[:2000],  # Limit description length
                        'required_skills': skills if skills else ['Remote Work'],
                        'location': job_data.get('location', 'Remote'),
                        'job_type': 'remote',
                        'source': 'remoteok',
                        'source_url': job_data.get('url', f"https://remoteok.com/remote-jobs/{job_data.get('slug', '')}"),
                        'source_job_id': str(job_data.get('id', '')),
                        'scraped_at': datetime.utcnow(),
                        'expires_at': datetime.utcnow() + timedelta(days=30),  # Assume 30 day expiry
                        'is_active': True
                    }
                    
                    jobs.append(job)
                    
                except Exception as e:
                    logger.warning(f"Error parsing RemoteOK job: {e}")
                    continue
            
            logger.info(f"Scraped {len(jobs)} jobs from RemoteOK")
            
        except Exception as e:
            logger.error(f"Error scraping RemoteOK: {e}")
        
        return jobs
    
    def scrape_adzuna(self, limit: int = 50, country: str = 'us') -> List[Dict]:
        """
        Scrape jobs from Adzuna API (requires free API key)
        Get API key from: https://developer.adzuna.com/
        """
        jobs = []
        try:
            # Note: You'll need to sign up for free API key
            # For now, returning empty to avoid API errors
            # Uncomment below and add your API credentials
            
            """
            app_id = "YOUR_APP_ID"  # Get from https://developer.adzuna.com/
            app_key = "YOUR_APP_KEY"
            
            url = f"https://api.adzuna.com/v1/api/jobs/{country}/search/1"
            params = {
                'app_id': app_id,
                'app_key': app_key,
                'results_per_page': limit,
                'what': 'developer software engineer',
                'content-type': 'application/json'
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            for job_data in data.get('results', []):
                try:
                    # Parse description to extract skills (basic implementation)
                    description = job_data.get('description', '')
                    skills = self._extract_skills_from_text(description)
                    
                    job = {
                        'title': job_data.get('title', 'Position'),
                        'company': job_data.get('company', {}).get('display_name', 'Company'),
                        'description': description[:2000],
                        'required_skills': skills,
                        'location': job_data.get('location', {}).get('display_name', 'Location'),
                        'job_type': self._categorize_job_type(job_data.get('contract_type', '')),
                        'source': 'adzuna',
                        'source_url': job_data.get('redirect_url', ''),
                        'source_job_id': job_data.get('id', ''),
                        'scraped_at': datetime.utcnow(),
                        'expires_at': datetime.utcnow() + timedelta(days=30),
                        'is_active': True
                    }
                    
                    jobs.append(job)
                    
                except Exception as e:
                    logger.warning(f"Error parsing Adzuna job: {e}")
                    continue
            
            logger.info(f"Scraped {len(jobs)} jobs from Adzuna")
            """
            
            logger.info("Adzuna scraper not configured (API key required)")
            
        except Exception as e:
            logger.error(f"Error scraping Adzuna: {e}")
        
        return jobs
    
    def _extract_skills_from_text(self, text: str) -> List[str]:
        """Extract common tech skills from job description"""
        common_skills = [
            'Python', 'JavaScript', 'Java', 'C++', 'C#', 'Ruby', 'Go', 'Rust', 'PHP', 'Swift',
            'React', 'Angular', 'Vue', 'Node.js', 'Django', 'Flask', 'Spring', 'Express',
            'AWS', 'Azure', 'GCP', 'Docker', 'Kubernetes', 'Jenkins', 'Git', 'CI/CD',
            'SQL', 'PostgreSQL', 'MySQL', 'MongoDB', 'Redis', 'Elasticsearch',
            'Machine Learning', 'AI', 'Data Science', 'NLP', 'Computer Vision',
            'REST API', 'GraphQL', 'Microservices', 'Agile', 'Scrum'
        ]
        
        text_lower = text.lower()
        found_skills = []
        
        for skill in common_skills:
            if skill.lower() in text_lower and skill not in found_skills:
                found_skills.append(skill)
        
        return found_skills[:15]  # Return max 15 skills
    
    def _categorize_job_type(self, contract_type: str) -> str:
        """Categorize job type from contract type string"""
        contract_lower = contract_type.lower()
        
        if 'full' in contract_lower or 'permanent' in contract_lower:
            return 'full-time'
        elif 'part' in contract_lower:
            return 'part-time'
        elif 'contract' in contract_lower or 'freelance' in contract_lower:
            return 'contract'
        elif 'intern' in contract_lower:
            return 'internship'
        else:
            return 'full-time'  # Default
    
    def save_jobs_to_db(self, jobs: List[Dict], db: Session) -> Dict[str, int]:
        """
        Save scraped jobs to database with deduplication
        Returns stats: {'added': X, 'updated': Y, 'skipped': Z}
        """
        stats = {'added': 0, 'updated': 0, 'skipped': 0}
        
        for job_data in jobs:
            try:
                # Check if job already exists by source_job_id
                existing_job = None
                if job_data.get('source_job_id'):
                    existing_job = db.query(Job).filter(
                        Job.source == job_data['source'],
                        Job.source_job_id == job_data['source_job_id']
                    ).first()
                
                if existing_job:
                    # Update existing job
                    existing_job.title = job_data['title']
                    existing_job.description = job_data['description']
                    existing_job.required_skills = job_data['required_skills']
                    existing_job.location = job_data['location']
                    existing_job.scraped_at = job_data['scraped_at']
                    existing_job.is_active = True
                    stats['updated'] += 1
                else:
                    # Generate embedding for new job
                    job_text = f"{job_data['title']} {job_data['company']} {job_data['description']} {' '.join(job_data['required_skills'])}"
                    embedding = self.ml_service.generate_embedding(job_text)
                    
                    # Create new job
                    new_job = Job(
                        title=job_data['title'],
                        company=job_data['company'],
                        description=job_data['description'],
                        required_skills=job_data['required_skills'],
                        location=job_data['location'],
                        job_type=job_data['job_type'],
                        embedding=embedding,
                        source=job_data['source'],
                        source_url=job_data['source_url'],
                        source_job_id=job_data['source_job_id'],
                        scraped_at=job_data['scraped_at'],
                        expires_at=job_data['expires_at'],
                        is_active=job_data['is_active']
                    )
                    
                    db.add(new_job)
                    stats['added'] += 1
                
                db.commit()
                
            except Exception as e:
                logger.error(f"Error saving job to DB: {e}")
                db.rollback()
                stats['skipped'] += 1
                continue
        
        return stats
    
    def mark_expired_jobs(self, db: Session) -> int:
        """Mark jobs as inactive if they've expired"""
        try:
            expired_count = db.query(Job).filter(
                Job.expires_at < datetime.utcnow(),
                Job.is_active == True
            ).update({'is_active': False})
            
            db.commit()
            logger.info(f"Marked {expired_count} jobs as expired")
            return expired_count
            
        except Exception as e:
            logger.error(f"Error marking expired jobs: {e}")
            db.rollback()
            return 0
    
    def scrape_all_sources(self, db: Session, limit_per_source: int = 50) -> Dict:
        """
        Scrape jobs from all configured sources
        Returns comprehensive stats
        """
        all_stats = {
            'sources_scraped': 0,
            'total_fetched': 0,
            'total_added': 0,
            'total_updated': 0,
            'total_skipped': 0,
            'errors': []
        }
        
        # Mark expired jobs first
        expired_count = self.mark_expired_jobs(db)
        all_stats['expired_marked'] = expired_count
        
        # Scrape from each source
        for source_name, scraper_func in self.sources.items():
            try:
                logger.info(f"Scraping {source_name}...")
                jobs = scraper_func(limit=limit_per_source)
                
                if jobs:
                    stats = self.save_jobs_to_db(jobs, db)
                    all_stats['sources_scraped'] += 1
                    all_stats['total_fetched'] += len(jobs)
                    all_stats['total_added'] += stats['added']
                    all_stats['total_updated'] += stats['updated']
                    all_stats['total_skipped'] += stats['skipped']
                
            except Exception as e:
                error_msg = f"Error scraping {source_name}: {str(e)}"
                logger.error(error_msg)
                all_stats['errors'].append(error_msg)
        
        all_stats['timestamp'] = datetime.utcnow().isoformat()
        return all_stats


# Singleton instance
job_scraper_service = JobScraperService()
