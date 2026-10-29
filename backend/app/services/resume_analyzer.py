"""
Resume Analyzer Service
Provides AI-powered suggestions to improve resume for specific jobs
"""

from typing import Dict, List
import re
from app.services.job_matcher import JobMatcher
import logging

logger = logging.getLogger(__name__)


class ResumeAnalyzerService:
    """Service for analyzing resumes and providing improvement suggestions"""

    def __init__(self):
        self.ml_service = JobMatcher()

    def analyze_resume_for_job(self, resume_text: str, job_description: str,
                                job_skills: List[str], resume_skills: List[str]) -> Dict:
        """
        Analyze resume against specific job and provide suggestions

        Returns comprehensive analysis with:
        - ATS score
        - Missing keywords
        - Tailored suggestions
        - Keyword density analysis
        """

        # Calculate ATS score
        ats_score = self._calculate_ats_score(resume_text, job_description, job_skills, resume_skills)

        # Find missing keywords
        missing_keywords = self._find_missing_keywords(resume_text, job_description, job_skills)

        # Find weak areas
        weak_areas = self._analyze_weak_areas(resume_text, job_description)

        # Generate specific suggestions
        suggestions = self._generate_suggestions(
            ats_score, missing_keywords, weak_areas, resume_skills, job_skills
        )

        # Keyword frequency analysis
        keyword_analysis = self._analyze_keyword_frequency(resume_text, job_skills)

        return {
            'ats_score': ats_score,
            'score_interpretation': self._interpret_score(ats_score),
            'missing_keywords': missing_keywords[:10],  # Top 10
            'weak_areas': weak_areas,
            'suggestions': suggestions,
            'keyword_analysis': keyword_analysis,
            'skill_match_rate': round(self.ml_service.analyze_skill_match(resume_skills, job_skills)[2] * 100, 1) if job_skills else 0,
            'recommended_additions': self._recommend_additions(missing_keywords, weak_areas)
        }

    def _calculate_ats_score(self, resume_text: str, job_description: str,
                             job_skills: List[str], resume_skills: List[str]) -> int:
        """
        Calculate ATS (Applicant Tracking System) score 0-100
        Based on keyword matching, skill overlap, and semantic similarity
        """
        resume_lower = resume_text.lower()

        # 1. Skills match (40 points)
        if job_skills:
            skill_match_score = self.ml_service.analyze_skill_match(resume_skills, job_skills)[2] * 40
        else:
            skill_match_score = 20

        # 2. Keyword frequency (30 points)
        important_keywords = self._extract_important_keywords(job_description)
        keyword_score = 0
        for keyword in important_keywords:
            if keyword.lower() in resume_lower:
                keyword_score += 1

        keyword_score = min((keyword_score / len(important_keywords)) * 30, 30) if important_keywords else 15

        # 3. Semantic similarity (30 points)
        try:
            resume_embedding = self.ml_service.generate_embedding(resume_text)
            job_embedding = self.ml_service.generate_embedding(job_description)
            similarity = self.ml_service.calculate_similarity(resume_embedding, job_embedding)
            semantic_score = similarity * 30
        except Exception:
            logger.exception("Semantic analysis failed")
            raise RuntimeError("Semantic analysis unavailable; no score was generated")

        total_score = int(skill_match_score + keyword_score + semantic_score)
        return min(max(total_score, 0), 100)  # Clamp between 0-100

    def _find_missing_keywords(self, resume_text: str, job_description: str,
                                job_skills: List[str]) -> List[str]:
        """Find important keywords from job description missing in resume"""
        resume_lower = resume_text.lower()
        missing = []

        # Check job skills
        for skill in job_skills:
            if skill.lower() not in resume_lower:
                missing.append(skill)

        # Extract important terms from job description
        important_terms = self._extract_important_keywords(job_description)
        for term in important_terms:
            if term.lower() not in resume_lower and term not in missing:
                missing.append(term)

        return missing[:15]  # Return top 15

    def _extract_important_keywords(self, text: str) -> List[str]:
        """Extract important keywords from text"""
        # Common important keywords in tech job descriptions
        important_patterns = [
            # Technical skills
            r'\b(Python|Java|JavaScript|C\+\+|Ruby|Go|Rust|PHP|Swift|Kotlin)\b',
            r'\b(React|Angular|Vue|Node\.js|Django|Flask|Spring|Express)\b',
            r'\b(AWS|Azure|GCP|Docker|Kubernetes|Jenkins|Git|CI/CD)\b',
            r'\b(SQL|PostgreSQL|MySQL|MongoDB|Redis|Elasticsearch)\b',
            r'\b(Machine Learning|AI|Data Science|NLP|Computer Vision)\b',
            r'\b(REST API|GraphQL|Microservices)\b',

            # Soft skills/requirements
            r'\b(leadership|team|collaboration|communication|problem[- ]solving)\b',
            r'\b(agile|scrum|kanban)\b',
            r'\b(bachelor|master|degree|PhD)\b',
            r'\b(\d+\+?\s*years?)\b',
        ]

        keywords = []

        for pattern in important_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            keywords.extend([m for m in matches if m])

        return list(set(keywords))[:20]

    def _analyze_weak_areas(self, resume_text: str, job_description: str) -> List[Dict]:
        """Analyze areas where resume is weak compared to job requirements"""
        weak_areas = []
        job_lower = job_description.lower()
        resume_lower = resume_text.lower()

        # Check for experience level
        experience_patterns = [
            (r'(\d+)\+?\s*years?\s*of\s*experience', 'experience_years'),
            (r'senior', 'seniority_level'),
            (r'lead|principal|staff', 'leadership_level'),
        ]

        for pattern, area_type in experience_patterns:
            job_matches = re.findall(pattern, job_lower)
            resume_matches = re.findall(pattern, resume_lower)

            if job_matches and not resume_matches:
                weak_areas.append({
                    'area': area_type,
                    'issue': f"Job requires {job_matches[0]} but resume doesn't clearly state this",
                    'severity': 'high'
                })

        # Check for specific sections
        required_sections = ['experience', 'education', 'skills', 'projects']
        for section in required_sections:
            if section not in resume_lower:
                weak_areas.append({
                    'area': section,
                    'issue': f"Resume may be missing '{section}' section",
                    'severity': 'medium'
                })

        return weak_areas[:5]

    def _analyze_keyword_frequency(self, resume_text: str, job_skills: List[str]) -> Dict:
        """Analyze how often key skills appear in resume"""
        resume_lower = resume_text.lower()
        frequency = {}

        for skill in job_skills:
            count = resume_lower.count(skill.lower())
            frequency[skill] = {
                'count': count,
                'status': 'good' if count >= 2 else 'needs_more' if count == 1 else 'missing'
            }

        return frequency

    def _generate_suggestions(self, ats_score: int, missing_keywords: List[str],
                              weak_areas: List[Dict], resume_skills: List[str],
                              job_skills: List[str]) -> List[Dict]:
        """Generate specific, actionable suggestions"""
        suggestions = []

        # Score-based suggestions
        if ats_score < 50:
            suggestions.append({
                'priority': 'critical',
                'category': 'overall',
                'title': 'Major Resume Overhaul Needed',
                'description': 'Your resume needs significant improvements to match this job. Focus on adding relevant keywords and skills.',
                'action': 'Consider restructuring your resume to highlight relevant experience'
            })
        elif ats_score < 70:
            suggestions.append({
                'priority': 'high',
                'category': 'overall',
                'title': 'Improve Keyword Matching',
                'description': 'Your resume is decent but needs more relevant keywords to pass ATS screening.',
                'action': 'Add more job-specific keywords throughout your experience and skills sections'
            })

        # Missing keywords suggestions
        if missing_keywords:
            top_missing = missing_keywords[:5]
            suggestions.append({
                'priority': 'high',
                'category': 'keywords',
                'title': 'Add Missing Key Skills',
                'description': f"These important skills are missing: {', '.join(top_missing)}",
                'action': f"If you have experience with {top_missing[0]}, add it prominently in your skills and experience sections"
            })

        # Skill match suggestions
        skill_match_rate = self.ml_service.analyze_skill_match(resume_skills, job_skills)[2] * 100 if job_skills else 0
        if skill_match_rate < 50:
            suggestions.append({
                'priority': 'high',
                'category': 'skills',
                'title': 'Low Skill Match Rate',
                'description': f"You only match {skill_match_rate:.0f}% of required skills",
                'action': 'Focus on gaining or highlighting experience with the required skills for this position'
            })

        # Weak area suggestions
        for weak_area in weak_areas[:3]:
            suggestions.append({
                'priority': weak_area['severity'],
                'category': weak_area['area'],
                'title': f"Improve {weak_area['area'].replace('_', ' ').title()}",
                'description': weak_area['issue'],
                'action': f"Add or emphasize your {weak_area['area'].replace('_', ' ')} in your resume"
            })

        return suggestions[:8]  # Return top 8 suggestions

    def _recommend_additions(self, missing_keywords: List[str],
                             weak_areas: List[Dict]) -> List[str]:
        """Quick list of recommended additions"""
        recommendations = []

        if missing_keywords:
            recommendations.append(f"Add these skills if applicable: {', '.join(missing_keywords[:3])}")

        if any(wa['area'] == 'experience_years' for wa in weak_areas):
            recommendations.append("Quantify your years of experience more clearly")

        if any(wa['area'] == 'projects' for wa in weak_areas):
            recommendations.append("Add a Projects section showcasing relevant work")

        recommendations.append("Use action verbs (Developed, Led, Implemented, Designed)")
        recommendations.append("Quantify achievements with numbers and percentages")

        return recommendations[:5]

    def _interpret_score(self, score: int) -> str:
        """Interpret ATS score into human-readable feedback"""
        if score >= 80:
            return "Excellent! Your resume is well-optimized for this job."
        elif score >= 70:
            return "Good! Your resume matches well, with room for minor improvements."
        elif score >= 50:
            return "Fair. Your resume needs some optimization to improve your chances."
        else:
            return "Needs Improvement. Significant changes recommended to match this job."


# Singleton instance
resume_analyzer_service = ResumeAnalyzerService()
