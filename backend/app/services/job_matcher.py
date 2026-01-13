from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from typing import List, Dict, Tuple
from app.config import settings


class JobMatcher:
    """Service for semantic job matching using embeddings."""
    
    def __init__(self):
        # Load the embedding model (lightweight and fast)
        self.model = SentenceTransformer(settings.EMBEDDING_MODEL)
    
    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding vector for given text."""
        embedding = self.model.encode(text)
        return embedding.tolist()
    
    def calculate_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """Calculate cosine similarity between two embeddings."""
        # Convert to numpy arrays
        vec1 = np.array(embedding1).reshape(1, -1)
        vec2 = np.array(embedding2).reshape(1, -1)
        
        # Calculate cosine similarity
        similarity = cosine_similarity(vec1, vec2)[0][0]
        return float(similarity)
    
    def prepare_resume_text(self, resume_data: Dict) -> str:
        """Prepare resume text for embedding generation."""
        parts = []
        
        # Add skills
        if resume_data.get('skills'):
            parts.append("Skills: " + ", ".join(resume_data['skills']))
        
        # Add education
        if resume_data.get('education'):
            edu_text = " ".join([edu.get('context', '') for edu in resume_data['education']])
            parts.append("Education: " + edu_text)
        
        # Add experience
        if resume_data.get('experience'):
            exp_text = " ".join([exp.get('context', '') for exp in resume_data['experience']])
            parts.append("Experience: " + exp_text)
        
        # Add raw text snippet (first 500 chars)
        if resume_data.get('raw_text'):
            parts.append(resume_data['raw_text'][:500])
        
        return " ".join(parts)
    
    def prepare_job_text(self, job_data: Dict) -> str:
        """Prepare job text for embedding generation."""
        parts = [
            f"Job Title: {job_data.get('title', '')}",
            f"Description: {job_data.get('description', '')}",
            f"Required Skills: {', '.join(job_data.get('required_skills', []))}"
        ]
        
        if job_data.get('company'):
            parts.append(f"Company: {job_data['company']}")
        
        return " ".join(parts)
    
    def analyze_skill_match(
        self, 
        candidate_skills: List[str], 
        required_skills: List[str]
    ) -> Tuple[List[str], List[str], float]:
        """
        Analyze skill overlap between candidate and job requirements.
        
        Returns:
            Tuple of (matching_skills, missing_skills, skill_match_percentage)
        """
        candidate_skills_lower = [s.lower() for s in candidate_skills]
        required_skills_lower = [s.lower() for s in required_skills]
        
        # Find matching skills
        matching_skills = [
            skill for skill in required_skills 
            if skill.lower() in candidate_skills_lower
        ]
        
        # Find missing skills
        missing_skills = [
            skill for skill in required_skills 
            if skill.lower() not in candidate_skills_lower
        ]
        
        # Calculate skill match percentage
        if required_skills:
            skill_match_percentage = len(matching_skills) / len(required_skills)
        else:
            skill_match_percentage = 0.0
        
        return matching_skills, missing_skills, skill_match_percentage
    
    def generate_explanation(
        self, 
        similarity_score: float,
        skill_match_percentage: float,
        matching_skills: List[str],
        missing_skills: List[str],
        job_title: str
    ) -> Dict:
        """Generate human-readable explanation for the match."""
        
        # Overall match quality
        if similarity_score >= 0.7:
            match_quality = "Excellent"
            recommendation = f"Highly recommended! You're a strong fit for this {job_title} role."
        elif similarity_score >= 0.5:
            match_quality = "Good"
            recommendation = f"Good match! You have relevant experience for this {job_title} role."
        elif similarity_score >= 0.3:
            match_quality = "Fair"
            recommendation = f"Fair match. Consider applying if you're interested in {job_title}."
        else:
            match_quality = "Low"
            recommendation = f"This role may not be the best fit, but you can still apply if interested."
        
        # Skill analysis
        skill_analysis = f"You match {len(matching_skills)} out of {len(matching_skills) + len(missing_skills)} required skills."
        
        # Generate detailed explanation
        explanation = {
            "match_quality": match_quality,
            "overall_score": round(similarity_score * 100, 1),  # Convert to percentage
            "skill_match_percentage": round(skill_match_percentage * 100, 1),
            "recommendation": recommendation,
            "skill_analysis": skill_analysis,
            "strengths": matching_skills[:5] if matching_skills else ["No specific skill matches found"],
            "areas_to_improve": missing_skills[:5] if missing_skills else ["No specific gaps identified"],
            "why_this_matches": self._generate_why_explanation(
                similarity_score, 
                skill_match_percentage,
                len(matching_skills)
            )
        }
        
        return explanation
    
    def _generate_why_explanation(
        self, 
        similarity_score: float,
        skill_match_percentage: float,
        matching_count: int
    ) -> str:
        """Generate 'why this job matches' explanation."""
        reasons = []
        
        if similarity_score >= 0.5:
            reasons.append("Your overall profile aligns well with this role")
        
        if skill_match_percentage >= 0.5:
            reasons.append(f"You have {matching_count} matching technical skills")
        
        if not reasons:
            reasons.append("Your background shows some relevant experience")
        
        return ". ".join(reasons) + "."
    
    def rank_jobs(
        self,
        resume_embedding: List[float],
        resume_skills: List[str],
        jobs: List[Dict],
        top_n: int = 10
    ) -> List[Dict]:
        """
        Rank jobs by relevance to resume.
        
        Args:
            resume_embedding: Embedding vector for resume
            resume_skills: List of candidate skills
            jobs: List of job dictionaries with embeddings and required_skills
            top_n: Number of top jobs to return
        
        Returns:
            List of jobs with match scores and explanations, sorted by relevance
        """
        matches = []
        
        for job in jobs:
            if not job.get('embedding'):
                continue
            
            # Calculate semantic similarity
            similarity_score = self.calculate_similarity(
                resume_embedding,
                job['embedding']
            )
            
            # Skip if below threshold
            if similarity_score < settings.SIMILARITY_THRESHOLD:
                continue
            
            # Analyze skill match
            matching_skills, missing_skills, skill_match_percentage = self.analyze_skill_match(
                resume_skills,
                job.get('required_skills', [])
            )
            
            # Generate explanation
            explanation = self.generate_explanation(
                similarity_score,
                skill_match_percentage,
                matching_skills,
                missing_skills,
                job.get('title', 'this position')
            )
            
            # Add to matches
            matches.append({
                'job': job,
                'similarity_score': similarity_score,
                'matching_skills': matching_skills,
                'missing_skills': missing_skills,
                'explanation': explanation
            })
        
        # Sort by similarity score (descending)
        matches.sort(key=lambda x: x['similarity_score'], reverse=True)
        
        return matches[:top_n]
